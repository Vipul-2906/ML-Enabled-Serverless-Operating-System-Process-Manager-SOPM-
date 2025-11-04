from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import json
import logging
import re
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
POSTGRES_HOST = 'postgres-service.sopm.svc.cluster.local'
POSTGRES_PORT = 5432
POSTGRES_DB = 'sopm'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'sopmpass123'

MINIO_HOST = 'minio-service.sopm.svc.cluster.local'
MINIO_PORT = 9000
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin'
MINIO_BUCKET = 'user-functions'

IMAGE_BUILDER_URL = 'http://image-builder-service.sopm.svc.cluster.local:8000'

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
    return jsonify({'status': 'healthy', 'service': 'function-registry'})

# ==================== CODE VALIDATION ====================

DANGEROUS_PATTERNS = [
    r'import\s+os\.system',
    r'import\s+subprocess',
    r'__import__\s*\(',
    r'eval\s*\(',
    r'exec\s*\(',
    r'compile\s*\(',
    r'open\s*\(',
    r'file\s*\(',
    r'input\s*\(',
    r'raw_input\s*\(',
]

ALLOWED_PACKAGES = {
    'requests', 'pandas', 'numpy', 'flask', 'fastapi',
    'textblob', 'pillow', 'qrcode', 'redis', 'psycopg2',
    'pymongo', 'sqlalchemy', 'pydantic', 'jinja2',
    'cryptography', 'jwt', 'bcrypt', 'passlib'
}

def validate_code(code: str, runtime: str) -> tuple:
    """Validate user code for security"""
    
    # Size limit
    if len(code) > 100000:  # 100KB
        return False, "Code exceeds 100KB limit"
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Dangerous pattern detected: {pattern}"
    
    # Syntax check for Python
    if runtime.startswith('python'):
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
    
    return True, "Valid"

def validate_dependencies(dependencies: str) -> tuple:
    """Validate requirements.txt"""
    
    if not dependencies:
        return True, "Valid"
    
    if len(dependencies) > 10000:  # 10KB limit
        return False, "Dependencies file too large"
    
    lines = dependencies.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Extract package name
        package = re.split('[=<>!]', line)[0].strip()
        
        if package not in ALLOWED_PACKAGES:
            return False, f"Package '{package}' not allowed. Allowed: {', '.join(sorted(ALLOWED_PACKAGES))}"
    
    return True, "Valid"

# ==================== MINIO STORAGE ====================

def store_code_in_minio(function_id: str, code: str) -> str:
    """Store code in MinIO and return reference"""
    from minio import Minio
    from io import BytesIO
    
    client = Minio(
        f"{MINIO_HOST}:{MINIO_PORT}",
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    
    # Ensure bucket exists
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
    
    # Store code
    code_path = f"functions/{function_id}/code.py"
    client.put_object(
        MINIO_BUCKET,
        code_path,
        BytesIO(code.encode('utf-8')),
        len(code.encode('utf-8'))
    )
    
    return code_path

def retrieve_code_from_minio(code_reference: str) -> str:
    """Retrieve code from MinIO"""
    from minio import Minio
    
    client = Minio(
        f"{MINIO_HOST}:{MINIO_PORT}",
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    
    response = client.get_object(MINIO_BUCKET, code_reference)
    return response.read().decode('utf-8')

# ==================== API ENDPOINTS ====================

@app.route('/functions', methods=['POST'])
def create_function():
    """Upload a new function"""
    try:
        data = request.json
        
        user_id = data.get('user_id')
        name = data.get('name')
        description = data.get('description', '')
        runtime = data.get('runtime', 'python3.11')
        code = data.get('code')
        dependencies = data.get('dependencies', '')
        memory_limit_mb = data.get('memory_limit_mb', 128)
        timeout_seconds = data.get('timeout_seconds', 30)
        
        # Validation
        if not all([user_id, name, code]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if runtime not in ['python3.11', 'python3.10', 'node18']:
            return jsonify({'error': 'Unsupported runtime'}), 400
        
        # Validate code
        valid, msg = validate_code(code, runtime)
        if not valid:
            return jsonify({'error': f'Code validation failed: {msg}'}), 400
        
        # Validate dependencies
        valid, msg = validate_dependencies(dependencies)
        if not valid:
            return jsonify({'error': f'Dependency validation failed: {msg}'}), 400
        
        # Create function record
        function_id = str(uuid.uuid4())
        
        # Store code in MinIO
        code_reference = store_code_in_minio(function_id, code)
        
        # Save to database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_functions 
            (id, user_id, name, description, runtime, code_reference, dependencies, 
             memory_limit_mb, timeout_seconds, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            RETURNING id
        """, (function_id, user_id, name, description, runtime, code_reference, 
              dependencies, memory_limit_mb, timeout_seconds))
        conn.commit()
        cur.close()
        conn.close()
        
        # Trigger image build
        try:
            build_response = requests.post(
                f"{IMAGE_BUILDER_URL}/build",
                json={
                    'function_id': function_id,
                    'runtime': runtime,
                    'code_reference': code_reference,
                    'dependencies': dependencies
                },
                timeout=5
            )
            
            if not build_response.ok:
                logger.error(f"Build trigger failed: {build_response.text}")
        except Exception as e:
            logger.error(f"Error triggering build: {str(e)}")
        
        logger.info(f"Function created: {function_id} ({name}) by {user_id}")
        
        return jsonify({
            'function_id': function_id,
            'status': 'pending',
            'message': 'Function submitted for building'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating function: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/functions/<function_id>', methods=['GET'])
def get_function(function_id):
    """Get function details"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, user_id, name, description, runtime, status, 
                   memory_limit_mb, timeout_seconds, image_url, error_message,
                   created_at, updated_at
            FROM user_functions
            WHERE id = %s
        """, (function_id,))
        function = cur.fetchone()
        cur.close()
        conn.close()
        
        if not function:
            return jsonify({'error': 'Function not found'}), 404
        
        return jsonify(function)
        
    except Exception as e:
        logger.error(f"Error getting function: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/functions', methods=['GET'])
def list_functions():
    """List user's functions"""
    try:
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if status:
            cur.execute("""
                SELECT id, name, description, runtime, status, created_at
                FROM user_functions
                WHERE user_id = %s AND status = %s
                ORDER BY created_at DESC
            """, (user_id, status))
        else:
            cur.execute("""
                SELECT id, name, description, runtime, status, created_at
                FROM user_functions
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
        
        functions = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'user_id': user_id,
            'count': len(functions),
            'functions': functions
        })
        
    except Exception as e:
        logger.error(f"Error listing functions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/functions/<function_id>', methods=['DELETE'])
def delete_function(function_id):
    """Delete a function"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM user_functions WHERE id = %s RETURNING id", (function_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if not deleted:
            return jsonify({'error': 'Function not found'}), 404
        
        logger.info(f"Function deleted: {function_id}")
        
        return jsonify({'message': 'Function deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting function: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/functions/<function_id>/executions', methods=['GET'])
def get_executions(function_id):
    """Get function execution history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, status, execution_time_ms, memory_used_mb, 
                   created_at, completed_at
            FROM function_executions
            WHERE function_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (function_id, limit))
        executions = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'function_id': function_id,
            'count': len(executions),
            'executions': executions
        })
        
    except Exception as e:
        logger.error(f"Error getting executions: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Function Registry service starting...")
    app.run(host='0.0.0.0', port=8000, debug=False)
