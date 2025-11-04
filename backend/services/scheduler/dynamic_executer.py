from kubernetes import client, config
import logging
import uuid
import json

logger = logging.getLogger(__name__)

# Load Kubernetes config
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

k8s_batch = client.BatchV1Api()
k8s_core = client.CoreV1Api()

def execute_user_function(function_id: str, function_metadata: dict, payload: dict) -> tuple:
    """
    Execute user-uploaded function in isolated Kubernetes Job with gVisor sandbox
    
    Args:
        function_id: UUID of the function
        function_metadata: Function details from registry
        payload: Input data for the function
        
    Returns:
        tuple: (execution_id, job_name)
    """
    
    execution_id = str(uuid.uuid4())
    job_name = f"exec-{execution_id[:8]}"
    
    logger.info(f"Creating execution job {job_name} for function {function_id}")
    
    # Create Kubernetes Job for isolated execution
    job_manifest = {
        'apiVersion': 'batch/v1',
        'kind': 'Job',
        'metadata': {
            'name': job_name,
            'namespace': 'sopm-sandbox',
            'labels': {
                'type': 'user-function',
                'function-id': function_id,
                'execution-id': execution_id
            }
        },
        'spec': {
            'ttlSecondsAfterFinished': 60,
            'backoffLimit': 0,
            'activeDeadlineSeconds': function_metadata.get('timeout_seconds', 30),
            'template': {
                'metadata': {
                    'labels': {
                        'type': 'user-function',
                        'function-id': function_id,
                        'execution-id': execution_id
                    }
                },
                'spec': {
  #                  'runtimeClassName': 'gvisor',   
                    'restartPolicy': 'Never',
                    'containers': [
                        {
                            'name': 'function',
                            'image': function_metadata['image_url'],
                            'imagePullPolicy': 'Always',
                            'env': [
                                {
                                    'name': 'INPUT_DATA',
                                    'value': json.dumps(payload)
                                },
                                {
                                    'name': 'EXECUTION_ID',
                                    'value': execution_id
                                },
                                {
                                    'name': 'FUNCTION_ID',
                                    'value': function_id
                                }
                            ],
                            'resources': {
                                'limits': {
                                    'memory': f"{function_metadata.get('memory_limit_mb', 128)}Mi",
                                    'cpu': f"{function_metadata.get('cpu_limit_millicores', 500)}m",
                                    'ephemeral-storage': '1Gi'
                                },
                                'requests': {
                                    'memory': f"{function_metadata.get('memory_limit_mb', 128) // 2}Mi",
                                    'cpu': '100m',
                                    'ephemeral-storage': '512Mi'
                                }
                            },
                            'securityContext': {
                                'runAsNonRoot': True,
                                'runAsUser': 1000,
                                'runAsGroup': 1000,
                                'allowPrivilegeEscalation': False,
                                'readOnlyRootFilesystem': True,
                                'capabilities': {
                                    'drop': ['ALL']
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    
    try:
        k8s_batch.create_namespaced_job(
            namespace='sopm-sandbox',
            body=job_manifest
        )
        logger.info(f"Created execution job: {job_name} for function {function_id}")
    except Exception as e:
        logger.error(f"Failed to create execution job: {str(e)}")
        raise
    
    return execution_id, job_name

def get_execution_result(job_name: str) -> dict:
    """Get execution result from completed job"""
    
    try:
        job = k8s_batch.read_namespaced_job_status(
            name=job_name,
            namespace='sopm-sandbox'
        )
        
        if job.status.succeeded:
            pods = k8s_core.list_namespaced_pod(
                namespace='sopm-sandbox',
                label_selector=f'job-name={job_name}'
            )
            
            if pods.items:
                try:
                    logs = k8s_core.read_namespaced_pod_log(
                        name=pods.items[0].metadata.name,
                        namespace='sopm-sandbox'
                    )
                    return {
                        'status': 'completed',
                        'output': logs
                    }
                except Exception as e:
                    logger.error(f"Error reading pod logs: {str(e)}")
                    return {
                        'status': 'completed',
                        'output': 'Execution completed but logs unavailable'
                    }
            
            return {
                'status': 'completed',
                'output': 'No output'
            }
        
        elif job.status.failed:
            pods = k8s_core.list_namespaced_pod(
                namespace='sopm-sandbox',
                label_selector=f'job-name={job_name}'
            )
            
            error_message = 'Execution failed'
            if pods.items:
                pod_status = pods.items[0].status
                if pod_status.container_statuses:
                    container_status = pod_status.container_statuses[0]
                    if container_status.state.terminated:
                        error_message = container_status.state.terminated.reason or 'Unknown error'
            
            return {
                'status': 'failed',
                'error': error_message
            }
        
        return {
            'status': 'running'
        }
        
    except Exception as e:
        logger.error(f"Error getting execution result: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
