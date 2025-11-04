from flask import Flask, request, jsonify
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import json
import time
import logging
from threading import Thread
from typing import List, Optional

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = 'redis-service.sopm.svc.cluster.local'
REDIS_PORT = 6379
POSTGRES_HOST = 'postgres-service.sopm.svc.cluster.local'
POSTGRES_PORT = 5432
POSTGRES_DB = 'sopm'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'sopmpass123'

# Worker service endpoints (K8s service will load balance)
WORKER_SERVICE = 'http://worker-service.sopm.svc.cluster.local:8080'
FUNCTION_REGISTRY_SERVICE = 'http://function-registry-service.sopm.svc.cluster.local:8000'

# Initialize connections
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    try:
        r.ping()
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'redis': 'connected', 'postgres': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# ==================== PRE-LOADED FUNCTIONS (Existing) ====================

@app.route('/submit', methods=['POST'])
def submit_job():
    """Submit a pre-loaded function job to the queue"""
    try:
        data = request.json
        function_name = data.get('function_name')
        payload = data.get('payload', {})
        
        if not function_name:
            return jsonify({'error': 'function_name is required'}), 400
        
        # Save to database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO jobs (function_name, payload, status)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (function_name, json.dumps(payload), 'pending')
        )
        job_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        # Push to Redis queue
        job_data = {
            'job_id': job_id,
            'function_name': function_name,
            'payload': payload,
            'type': 'pre-loaded'
        }
        r.lpush('job_queue', json.dumps(job_data))
        
        logger.info(f"Job {job_id} submitted: {function_name}")
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'function_name': function_name
        }), 201
        
    except Exception as e:
        logger.error(f"Error submitting job: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== USER-UPLOADED FUNCTIONS (NEW) ====================

@app.route('/submit-user-function', methods=['POST'])
def submit_user_function_job():
    """Submit a user-uploaded function job"""
    try:
        data = request.json
        function_id = data.get('function_id')
        payload = data.get('payload', {})
        
        if not function_id:
            return jsonify({'error': 'function_id is required'}), 400
        
        # Get function metadata from registry
        try:
            func_response = requests.get(
                f"{FUNCTION_REGISTRY_SERVICE}/functions/{function_id}",
                timeout=5
            )
            
            if not func_response.ok:
                return jsonify({'error': 'Function not found or not ready'}), 404
            
            function_metadata = func_response.json()
            
            if function_metadata['status'] != 'ready':
                return jsonify({
                    'error': f"Function not ready. Status: {function_metadata['status']}"
                }), 400
                
        except Exception as e:
            logger.error(f"Error getting function metadata: {str(e)}")
            return jsonify({'error': 'Could not retrieve function metadata'}), 500
        
        # Save to jobs database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO jobs (function_name, payload, status)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (f"user_function_{function_id}", json.dumps(payload), 'pending')
        )
        job_id = cur.fetchone()[0]
        conn.commit()
        
        # Also save to function_executions
        cur.execute(
            """
            INSERT INTO function_executions (function_id, job_id, status, input_data)
            VALUES (%s, %s, %s, %s)
            """,
            (function_id, job_id, 'pending', json.dumps(payload))
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Push to Redis queue for user functions
        job_data = {
            'job_id': job_id,
            'function_id': function_id,
            'function_metadata': function_metadata,
            'payload': payload,
            'type': 'user-uploaded'
        }
        r.lpush('user_function_queue', json.dumps(job_data))
        
        logger.info(f"User function job {job_id} submitted: {function_id}")
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'function_id': function_id,
            'function_name': function_metadata['name']
        }), 201
        
    except Exception as e:
        logger.error(f"Error submitting user function job: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== COMMON STATUS/MONITORING ====================

@app.route('/status/<int:job_id>', methods=['GET'])
def get_status(job_id):
    """Get job status"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT id, function_name, status, result, execution_time_ms,
                   created_at, completed_at
            FROM jobs
            WHERE id = %s
            """,
            (job_id,)
        )
        job = cur.fetchone()
        cur.close()
        conn.close()
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Parse result if it's JSON
        result = job['result']
        if result:
            try:
                result = json.loads(result)
            except:
                pass
        
        return jsonify({
            'job_id': job['id'],
            'function_name': job['function_name'],
            'status': job['status'],
            'result': result,
            'execution_time_ms': job['execution_time_ms'],
            'created_at': job['created_at'].isoformat() if job['created_at'] else None,
'completed_at': job['completed_at'].isoformat() if job['completed_at'] else None
        })
        
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List recent jobs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        status = request.args.get('status', None)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if status:
            cur.execute(
                """
                SELECT id, function_name, status, execution_time_ms, created_at
                FROM jobs
                WHERE status = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (status, limit)
            )
        else:
            cur.execute(
                """
                SELECT id, function_name, status, execution_time_ms, created_at
                FROM jobs
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,)
            )
        
        jobs = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'total': len(jobs),
            'jobs': jobs
        })
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get status counts
        cur.execute("""
            SELECT status, COUNT(*) as count
            FROM jobs
            GROUP BY status
        """)
        status_counts = {row['status']: row['count'] for row in cur.fetchall()}
        
        # Get average execution time
        cur.execute("""
            SELECT AVG(execution_time_ms) as avg_time
            FROM jobs
            WHERE status = 'completed' AND execution_time_ms IS NOT NULL
        """)
        avg_time = cur.fetchone()['avg_time']
        
        # Get queue sizes
        pre_loaded_queue_size = r.llen('job_queue')
        user_function_queue_size = r.llen('user_function_queue')
        
        # Get user function stats
        cur.execute("""
            SELECT COUNT(*) as total_user_functions
            FROM user_functions
            WHERE status = 'ready'
        """)
        user_functions_ready = cur.fetchone()['total_user_functions']
        
        cur.close()
        conn.close()
        
        return jsonify({
            'status_counts': status_counts,
            'average_execution_time_ms': round(float(avg_time), 2) if avg_time else 0,
            'pre_loaded_queue_size': pre_loaded_queue_size,
            'user_function_queue_size': user_function_queue_size,
            'user_functions_ready': user_functions_ready
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== DISPATCHER LOOPS ====================

def pre_loaded_dispatcher_loop():
    """Background thread that dispatches pre-loaded function jobs to workers"""
    logger.info("Pre-loaded function dispatcher loop started")
    
    while True:
        try:
            # Blocking pop from Redis queue (waits 1 second)
            job_data = r.brpop('job_queue', timeout=1)
            
            if not job_data:
                continue
            
            job = json.loads(job_data[1])
            job_id = job['job_id']
            function_name = job['function_name']
            payload = job['payload']
            
            logger.info(f"Dispatching pre-loaded job {job_id}: {function_name}")
            
            # Update status to running
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE jobs SET status = 'running' WHERE id = %s",
                (job_id,)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            # Execute on worker
            start_time = time.time()
            try:
                response = requests.post(
                    f"{WORKER_SERVICE}/execute",
                    json={
                        'function_name': function_name,
                        'payload': payload
                    },
                    timeout=30
                )
                
                execution_time = (time.time() - start_time) * 1000
                
                conn = get_db_connection()
                cur = conn.cursor()
                
                if response.ok:
                    result = response.json()
                    cur.execute(
                        """
                        UPDATE jobs 
                        SET status = 'completed', 
                            result = %s, 
                            execution_time_ms = %s,
                            completed_at = NOW()
                        WHERE id = %s
                        """,
                        (json.dumps(result), execution_time, job_id)
                    )
                    logger.info(f"Pre-loaded job {job_id} completed in {execution_time:.2f}ms")
                else:
                    cur.execute(
                        """
                        UPDATE jobs 
                        SET status = 'failed', 
                            result = %s,
                            completed_at = NOW()
                        WHERE id = %s
                        """,
                        (json.dumps({'error': response.text}), job_id)
                    )
                    logger.error(f"Pre-loaded job {job_id} failed: {response.text}")
                
                conn.commit()
                cur.close()
                conn.close()
                
            except Exception as e:
                logger.error(f"Error executing pre-loaded job {job_id}: {str(e)}")
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE jobs 
                    SET status = 'failed', 
                        result = %s,
                        completed_at = NOW()
                    WHERE id = %s
                    """,
                    (json.dumps({'error': str(e)}), job_id)
                )
                conn.commit()
                cur.close()
                conn.close()
                
        except Exception as e:
            logger.error(f"Pre-loaded dispatcher loop error: {str(e)}")
            time.sleep(1)

def user_function_dispatcher_loop():
    """Background thread that dispatches user function jobs using dynamic executors"""
    logger.info("User function dispatcher loop started")
    
    # Import dynamic executor
    from dynamic_executer import execute_user_function, get_execution_result
    
    while True:
        try:
            # Blocking pop from Redis queue (waits 1 second)
            job_data = r.brpop('user_function_queue', timeout=1)
            
            if not job_data:
                continue
            
            job = json.loads(job_data[1])
            job_id = job['job_id']
            function_id = job['function_id']
            function_metadata = job['function_metadata']
            payload = job['payload']
            
            logger.info(f"Dispatching user function job {job_id}: {function_id}")
            
            # Update status to running
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE jobs SET status = 'running' WHERE id = %s",
                (job_id,)
            )
            cur.execute(
                "UPDATE function_executions SET status = 'running' WHERE job_id = %s",
                (job_id,)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            # Execute using dynamic Kubernetes Job
            start_time = time.time()
            try:
                execution_id, job_name = execute_user_function(
                    function_id, 
                    function_metadata, 
                    payload
                )
                
                # Monitor execution (with timeout)
                max_wait = function_metadata.get('timeout_seconds', 30) + 10
                elapsed = 0
                interval = 2
                
                while elapsed < max_wait:
                    result = get_execution_result(job_name)
                    
                    if result['status'] == 'completed':
                        execution_time = (time.time() - start_time) * 1000
                        
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute(
                            """
                            UPDATE jobs 
                            SET status = 'completed', 
                                result = %s, 
                                execution_time_ms = %s,
                                completed_at = NOW()
                            WHERE id = %s
                            """,
                            (json.dumps({'output': result['output']}), execution_time, job_id)
                        )
                        cur.execute(
                            """
                            UPDATE function_executions 
                            SET status = 'completed', 
                                output_data = %s,
                                execution_time_ms = %s,
                                completed_at = NOW()
                            WHERE job_id = %s
                            """,
                            (result['output'], execution_time, job_id)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        
                        logger.info(f"User function job {job_id} completed in {execution_time:.2f}ms")
                        break
                        
                    elif result['status'] == 'failed':
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute(
                            """
                            UPDATE jobs 
                            SET status = 'failed', 
                                result = %s,
                                completed_at = NOW()
                            WHERE id = %s
                            """,
                            (json.dumps({'error': result.get('error', 'Execution failed')}), job_id)
                        )
                        cur.execute(
                            """
                            UPDATE function_executions 
                            SET status = 'failed', 
                                error_message = %s,
                                completed_at = NOW()
                            WHERE job_id = %s
                            """,
                            (result.get('error', 'Execution failed'), job_id)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        
                        logger.error(f"User function job {job_id} failed")
                        break
                    
                    time.sleep(interval)
                    elapsed += interval
                
                # Timeout
                if elapsed >= max_wait:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute(
                        """
                        UPDATE jobs 
                        SET status = 'failed', 
                            result = %s,
                            completed_at = NOW()
                        WHERE id = %s
                        """,
                        (json.dumps({'error': 'Execution timeout'}), job_id)
                    )
                    cur.execute(
                        """
                        UPDATE function_executions 
                        SET status = 'failed', 
                            error_message = 'Execution timeout',
                            completed_at = NOW()
                        WHERE job_id = %s
                        """,
                        (job_id,)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    logger.error(f"User function job {job_id} timed out")
                
            except Exception as e:
                logger.error(f"Error executing user function job {job_id}: {str(e)}")
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE jobs 
                    SET status = 'failed', 
                        result = %s,
                        completed_at = NOW()
                    WHERE id = %s
                    """,
                    (json.dumps({'error': str(e)}), job_id)
                )
                cur.execute(
                    """
                    UPDATE function_executions 
                    SET status = 'failed', 
                        error_message = %s,
                        completed_at = NOW()
                    WHERE job_id = %s
                    """,
                    (str(e), job_id)
                )
                conn.commit()
                cur.close()
                conn.close()
                
        except Exception as e:
            logger.error(f"User function dispatcher loop error: {str(e)}")
            time.sleep(1)

if __name__ == '__main__':
    # Start both dispatcher threads
    pre_loaded_thread = Thread(target=pre_loaded_dispatcher_loop, daemon=True)
    pre_loaded_thread.start()
    
    user_function_thread = Thread(target=user_function_dispatcher_loop, daemon=True)
    user_function_thread.start()
    
    logger.info("Scheduler service starting with dual dispatchers...")
    app.run(host='0.0.0.0', port=8000, debug=False)