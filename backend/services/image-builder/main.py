from flask import Flask, request, jsonify
import logging
import os
import yaml
from kubernetes import client, config
import psycopg2
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Kubernetes config
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

k8s_batch = client.BatchV1Api()

# Configuration
POSTGRES_HOST = 'postgres-service.sopm.svc.cluster.local'
POSTGRES_DB = 'sopm'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'sopmpass123'

REGISTRY_URL = 'registry-service.sopm.svc.cluster.local:5000'
MINIO_HOST = 'minio-service.sopm.svc.cluster.local'

def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'image-builder'})

def generate_dockerfile(runtime: str, dependencies: str) -> str:
    """Generate Dockerfile based on runtime"""
    
    if runtime == 'python3.11':
        dockerfile = f"""
FROM python:3.11-slim

# Security: Run as non-root user
RUN useradd -m -u 1000 funcuser
WORKDIR /home/funcuser/app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy function code
COPY function.py .

# Switch to non-root user
USER funcuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/home/funcuser/.local/bin:$PATH"

# Entrypoint
CMD ["python", "function.py"]
"""
    elif runtime == 'python3.10':
        dockerfile = f"""
FROM python:3.10-slim

RUN useradd -m -u 1000 funcuser
WORKDIR /home/funcuser/app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY function.py .

USER funcuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/home/funcuser/.local/bin:$PATH"

CMD ["python", "function.py"]
"""
    elif runtime == 'node18':
        dockerfile = f"""
FROM node:18-slim

RUN useradd -m -u 1000 funcuser
WORKDIR /home/funcuser/app

COPY package.json .
RUN npm install --production

COPY function.js .

USER funcuser

CMD ["node", "function.js"]
"""
    else:
        raise ValueError(f"Unsupported runtime: {runtime}")
    
    return dockerfile

def create_kaniko_job(function_id: str, runtime: str, code_reference: str, dependencies: str):
    """Create Kubernetes Job to build image using Kaniko"""
    
    job_name = f"build-{function_id[:8]}"
    image_tag = f"{REGISTRY_URL}/{function_id}:latest"
    
    # Generate Dockerfile
    dockerfile_content = generate_dockerfile(runtime, dependencies)
    
    # Create ConfigMap with build context
    configmap_manifest = {
        'apiVersion': 'v1',
        'kind': 'ConfigMap',
        'metadata': {
            'name': f'build-context-{function_id[:8]}',
            'namespace': 'sopm'
        },
        'data': {
            'Dockerfile': dockerfile_content,
            'requirements.txt': dependencies if dependencies else '# No dependencies'
        }
    }
    
    k8s_core = client.CoreV1Api()
    
    # Delete existing ConfigMap if exists
    try:
        k8s_core.delete_namespaced_config_map(
            name=f'build-context-{function_id[:8]}',
            namespace='sopm'
        )
        time.sleep(1)
    except:
        pass
    
    # Create ConfigMap
    k8s_core.create_namespaced_config_map(
        namespace='sopm',
        body=configmap_manifest
    )
    
    # Create Kaniko Job
    job_manifest = {
        'apiVersion': 'batch/v1',
        'kind': 'Job',
        'metadata': {
            'name': job_name,
            'namespace': 'sopm'
        },
        'spec': {
            'ttlSecondsAfterFinished': 300,
            'backoffLimit': 2,
            'template': {
                'metadata': {
                    'labels': {
                        'app': 'kaniko-builder',
                        'function-id': function_id
                    }
                },
                'spec': {
                    'serviceAccountName': 'builder-sa',
                    'restartPolicy': 'Never',
                    'initContainers': [
                        {
                            'name': 'fetch-code',
                            'image': 'minio/mc:latest',
                            'command': ['/bin/sh', '-c'],
                            'args': [
                                f'''
                                mc alias set minio http://{MINIO_HOST}:9000 minioadmin minioadmin
                                mc cp minio/user-functions/{code_reference} /workspace/function.py
                                '''
                            ],
                            'volumeMounts': [
                                {
                                    'name': 'workspace',
                                    'mountPath': '/workspace'
                                }
                            ]
                        }
                    ],
                    'containers': [
                        {
                            'name': 'kaniko',
                            'image': 'gcr.io/kaniko-project/executor:v1.9.0',
                            'args': [
                                f'--dockerfile=/workspace/Dockerfile',
                                f'--context=/workspace',
                                f'--destination={image_tag}',
                                '--insecure',
                                '--skip-tls-verify',
                                '--cache=false'
                            ],
                            'volumeMounts': [
                                {
                                    'name': 'workspace',
                                    'mountPath': '/workspace'
                                },
                                {
                                    'name': 'build-context',
                                    'mountPath': '/workspace/Dockerfile',
                                    'subPath': 'Dockerfile'
                                },
                                {
                                    'name': 'build-context',
                                    'mountPath': '/workspace/requirements.txt',
                                    'subPath': 'requirements.txt'
                                }
                            ]
                        }
                    ],
                    'volumes': [
                        {
                            'name': 'workspace',
                            'emptyDir': {}
                        },
                        {
                            'name': 'build-context',
                            'configMap': {
                                'name': f'build-context-{function_id[:8]}'
                            }
                        }
                    ]
                }
            }
        }
    }
    
    # Delete existing job if exists
    try:
        k8s_batch.delete_namespaced_job(
            name=job_name,
            namespace='sopm',
            propagation_policy='Background'
        )
        time.sleep(2)
    except:
        pass
    
    # Create job
    k8s_batch.create_namespaced_job(
        namespace='sopm',
        body=job_manifest
    )
    
    logger.info(f"Kaniko build job created: {job_name} for function {function_id}")
    
    return job_name, image_tag

@app.route('/build', methods=['POST'])
def trigger_build():
    """Trigger image build for a function"""
    try:
        data = request.json
        
        function_id = data.get('function_id')
        runtime = data.get('runtime')
        code_reference = data.get('code_reference')
        dependencies = data.get('dependencies', '')
        
        if not all([function_id, runtime, code_reference]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        logger.info(f"Starting build for function: {function_id}")
        
        # Update function status to building
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE user_functions 
            SET status = 'building', updated_at = NOW()
            WHERE id = %s
        """, (function_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        # Create Kaniko build job
        job_name, image_tag = create_kaniko_job(
            function_id, runtime, code_reference, dependencies
        )
        
        # Start background thread to monitor build
        from threading import Thread
        Thread(target=monitor_build, args=(function_id, job_name, image_tag), daemon=True).start()
        
        return jsonify({
            'function_id': function_id,
            'job_name': job_name,
            'status': 'building'
        }), 202
        
    except Exception as e:
        logger.error(f"Error triggering build: {str(e)}")
        return jsonify({'error': str(e)}), 500

def monitor_build(function_id: str, job_name: str, image_tag: str):
    """Monitor build job and update function status"""
    max_wait = 600  # 10 minutes
    interval = 5
    elapsed = 0
    
    while elapsed < max_wait:
        try:
            # Check job status
            job = k8s_batch.read_namespaced_job_status(
                name=job_name,
                namespace='sopm'
            )
            
            if job.status.succeeded:
                # Build succeeded
                logger.info(f"Build succeeded for function: {function_id}")
                
                # Update function status
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE user_functions 
                    SET status = 'ready', 
                        image_url = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (image_tag, function_id))
                conn.commit()
                cur.close()
                conn.close()
                
                break
                
            elif job.status.failed:
                # Build failed
                logger.error(f"Build failed for function: {function_id}")
                
                # Get error logs
                k8s_core = client.CoreV1Api()
                pods = k8s_core.list_namespaced_pod(
                    namespace='sopm',
                    label_selector=f'job-name={job_name}'
                )
                
                error_message = "Build failed"
                if pods.items:
                    try:
                        logs = k8s_core.read_namespaced_pod_log(
                            name=pods.items[0].metadata.name,
                            namespace='sopm',
                            container='kaniko'
                        )
                        error_message = logs[-1000:]  # Last 1000 chars
                    except:
                        pass
                
                # Update function status
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE user_functions 
                    SET status = 'failed', 
                        error_message = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (error_message, function_id))
                conn.commit()
                cur.close()
                conn.close()
                
                break
            
            time.sleep(interval)
            elapsed += interval
            
        except Exception as e:
            logger.error(f"Error monitoring build: {str(e)}")
            break
    
    if elapsed >= max_wait:
        # Timeout
        logger.error(f"Build timeout for function: {function_id}")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE user_functions 
            SET status = 'failed', 
                error_message = 'Build timeout',
                updated_at = NOW()
            WHERE id = %s
        """, (function_id,))
        conn.commit()
        cur.close()
        conn.close()

if __name__ == '__main__':
    logger.info("Image Builder service starting...")
    app.run(host='0.0.0.0', port=8000, debug=False)
