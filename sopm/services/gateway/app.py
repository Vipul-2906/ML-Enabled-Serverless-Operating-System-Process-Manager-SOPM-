from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service endpoints
SCHEDULER_SERVICE = 'http://scheduler-service.sopm.svc.cluster.local:8000'
FUNCTION_REGISTRY_SERVICE = 'http://function-registry-service.sopm.svc.cluster.local:8000'

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'gateway'})

# ==================== PRE-LOADED FUNCTIONS (Existing) ====================

@app.route('/api/functions', methods=['GET'])
def list_functions():
    """List all available pre-loaded functions"""
    functions = {
        'data_processing': [
            {'name': 'csv_parser', 'description': 'Parse CSV and return summary statistics'},
            {'name': 'json_validator', 'description': 'Validate JSON structure'},
            {'name': 'data_aggregator', 'description': 'Aggregate data by column'},
            {'name': 'data_filter', 'description': 'Filter data based on conditions'},
            {'name': 'data_sorter', 'description': 'Sort data by column'},
            {'name': 'deduplicator', 'description': 'Remove duplicate rows'},
            {'name': 'data_merger', 'description': 'Merge two datasets'},
            {'name': 'column_renamer', 'description': 'Rename columns in dataset'},
            {'name': 'missing_value_handler', 'description': 'Handle missing values'},
            {'name': 'data_transpose', 'description': 'Transpose dataset'},
            {'name': 'column_selector', 'description': 'Select specific columns'},
            {'name': 'row_slicer', 'description': 'Slice rows from dataset'},
            {'name': 'data_groupby', 'description': 'Group and aggregate data'},
            {'name': 'csv_to_json', 'description': 'Convert CSV to JSON'},
            {'name': 'json_to_csv', 'description': 'Convert JSON to CSV'},
            {'name': 'data_pivot', 'description': 'Pivot data table'},
            {'name': 'data_describe', 'description': 'Statistical description'},
            {'name': 'column_dropper', 'description': 'Drop specified columns'},
            {'name': 'data_sampler', 'description': 'Sample random rows'},
            {'name': 'value_counter', 'description': 'Count unique values'}
        ],
        'text_analysis': [
            {'name': 'sentiment_analysis', 'description': 'Analyze text sentiment'},
            {'name': 'word_counter', 'description': 'Count word frequency'},
            {'name': 'text_summarizer', 'description': 'Summarize text'},
            {'name': 'language_detector', 'description': 'Detect text language'},
            {'name': 'spam_detector', 'description': 'Detect spam content'},
            {'name': 'text_cleaner', 'description': 'Clean and normalize text'},
            {'name': 'keyword_extractor', 'description': 'Extract keywords'},
            {'name': 'character_counter', 'description': 'Count characters, words, sentences'},
            {'name': 'text_case_converter', 'description': 'Convert text case'},
            {'name': 'text_reverser', 'description': 'Reverse text'},
            {'name': 'palindrome_checker', 'description': 'Check if palindrome'},
            {'name': 'vowel_counter', 'description': 'Count vowels and consonants'},
            {'name': 'text_splitter', 'description': 'Split text by delimiter'},
            {'name': 'text_replacer', 'description': 'Replace text'},
            {'name': 'email_extractor', 'description': 'Extract email addresses'},
            {'name': 'url_extractor', 'description': 'Extract URLs'},
            {'name': 'phone_extractor', 'description': 'Extract phone numbers'},
            {'name': 'text_truncator', 'description': 'Truncate text'},
            {'name': 'word_replacer', 'description': 'Replace specific words'},
            {'name': 'text_diff', 'description': 'Find text differences'}
        ],
        'math_compute': [
            {'name': 'prime_checker', 'description': 'Check if number is prime'},
            {'name': 'fibonacci_generator', 'description': 'Generate Fibonacci sequence'},
            {'name': 'factorial_calculator', 'description': 'Calculate factorial'},
            {'name': 'gcd_calculator', 'description': 'Calculate GCD'},
            {'name': 'lcm_calculator', 'description': 'Calculate LCM'},
            {'name': 'power_calculator', 'description': 'Calculate power'},
            {'name': 'square_root_calculator', 'description': 'Calculate square root'},
            {'name': 'logarithm_calculator', 'description': 'Calculate logarithm'},
            {'name': 'percentage_calculator', 'description': 'Calculate percentage'},
            {'name': 'average_calculator', 'description': 'Calculate average'},
            {'name': 'median_calculator', 'description': 'Calculate median'},
            {'name': 'mode_calculator', 'description': 'Calculate mode'},
            {'name': 'standard_deviation_calculator', 'description': 'Calculate std deviation'},
            {'name': 'range_calculator', 'description': 'Calculate range'},
            {'name': 'combination_calculator', 'description': 'Calculate nCr'},
            {'name': 'permutation_calculator', 'description': 'Calculate nPr'},
            {'name': 'trigonometry_calculator', 'description': 'Calculate trig functions'},
            {'name': 'absolute_value', 'description': 'Calculate absolute value'},
            {'name': 'rounding_calculator', 'description': 'Round numbers'},
            {'name': 'distance_calculator', 'description': 'Calculate distance between points'}
        ],
        'api_integrations': [
            {'name': 'weather_fetcher', 'description': 'Get weather data'},
            {'name': 'ip_geolocation', 'description': 'Get IP geolocation'},
            {'name': 'url_shortener_info', 'description': 'Generate short URL info'},
            {'name': 'random_quote_generator', 'description': 'Get inspirational quotes'},
            {'name': 'random_user_generator', 'description': 'Generate random user data'},
            {'name': 'cat_fact_fetcher', 'description': 'Get random cat facts'},
            {'name': 'dog_image_fetcher', 'description': 'Get random dog image'},
            {'name': 'joke_generator', 'description': 'Get random jokes'},
            {'name': 'advice_generator', 'description': 'Get random advice'},
            {'name': 'github_user_info', 'description': 'Get GitHub user info'},
            {'name': 'cryptocurrency_price', 'description': 'Get crypto prices'},
            {'name': 'country_info', 'description': 'Get country information'},
            {'name': 'number_facts', 'description': 'Get number facts'},
            {'name': 'json_placeholder_post', 'description': 'Get sample posts'},
            {'name': 'bored_activity', 'description': 'Get activity suggestions'},
            {'name': 'university_search', 'description': 'Search universities'},
            {'name': 'gender_predictor', 'description': 'Predict gender from name'},
            {'name': 'age_predictor', 'description': 'Predict age from name'},
            {'name': 'nationality_predictor', 'description': 'Predict nationality from name'},
            {'name': 'public_ip_fetcher', 'description': 'Get public IP address'}
        ],
        'utilities': [
            {'name': 'hash_generator', 'description': 'Generate MD5/SHA hashes'},
            {'name': 'base64_encoder', 'description': 'Encode to base64'},
            {'name': 'base64_decoder', 'description': 'Decode from base64'},
            {'name': 'qr_code_generator', 'description': 'Generate QR codes'},
            {'name': 'password_generator', 'description': 'Generate secure passwords'},
            {'name': 'uuid_generator', 'description': 'Generate UUIDs'},
            {'name': 'timestamp_converter', 'description': 'Convert timestamps'},
            {'name': 'calculator', 'description': 'Perform calculations'},
            {'name': 'json_formatter', 'description': 'Format JSON with indentation'},
            {'name': 'json_minifier', 'description': 'Minify JSON'},
            {'name': 'hex_to_rgb', 'description': 'Convert HEX to RGB'},
            {'name': 'rgb_to_hex', 'description': 'Convert RGB to HEX'},
            {'name': 'random_number_generator', 'description': 'Generate random numbers'},
            {'name': 'string_to_binary', 'description': 'Convert string to binary'},
            {'name': 'binary_to_string', 'description': 'Convert binary to string'},
            {'name': 'url_encoder', 'description': 'URL encode text'},
            {'name': 'url_decoder', 'description': 'URL decode text'},
            {'name': 'string_sorter', 'description': 'Sort strings'},
            {'name': 'list_shuffler', 'description': 'Shuffle lists'}
        ]
    }
    
    total = sum(len(funcs) for funcs in functions.values())
    
    return jsonify({
        'total_functions': total,
        'categories': functions,
        'type': 'pre-loaded'
    })

@app.route('/api/execute', methods=['POST'])
def execute_function():
    """Execute a pre-loaded function"""
    try:
        data = request.json
        
        if not data or 'function_name' not in data:
            return jsonify({'error': 'function_name is required'}), 400
        
        logger.info(f"Executing function: {data['function_name']}")
        
        # Forward to scheduler
        response = requests.post(
            f"{SCHEDULER_SERVICE}/submit",
            json=data,
            timeout=5
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Scheduler service timeout'}), 504
    except Exception as e:
        logger.error(f"Error executing function: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<int:job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    try:
        response = requests.get(
            f"{SCHEDULER_SERVICE}/status/{job_id}",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Scheduler service timeout'}), 504
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List recent jobs"""
    try:
        limit = request.args.get('limit', 50)
        status = request.args.get('status', None)
        
        params = {'limit': limit}
        if status:
            params['status'] = status
        
        response = requests.get(
            f"{SCHEDULER_SERVICE}/jobs",
            params=params,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Scheduler service timeout'}), 504
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        response = requests.get(
            f"{SCHEDULER_SERVICE}/stats",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Scheduler service timeout'}), 504
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== USER-UPLOADED FUNCTIONS (NEW) ====================

@app.route('/api/user-functions', methods=['POST'])
def upload_user_function():
    """Upload a new user function"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['user_id', 'name', 'code', 'runtime']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        logger.info(f"Uploading user function: {data['name']} by {data['user_id']}")
        
        # Forward to function registry
        response = requests.post(
            f"{FUNCTION_REGISTRY_SERVICE}/functions",
            json=data,
            timeout=10
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Function registry service timeout'}), 504
    except Exception as e:
        logger.error(f"Error uploading user function: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-functions', methods=['GET'])
def list_user_functions():
    """List user's uploaded functions"""
    try:
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        
        if not user_id:
            return jsonify({'error': 'user_id parameter required'}), 400
        
        params = {'user_id': user_id}
        if status:
            params['status'] = status
        
        response = requests.get(
            f"{FUNCTION_REGISTRY_SERVICE}/functions",
            params=params,
            timeout=5
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Function registry service timeout'}), 504
    except Exception as e:
        logger.error(f"Error listing user functions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-functions/<function_id>', methods=['GET'])
def get_user_function(function_id):
    """Get user function details"""
    try:
        response = requests.get(
            f"{FUNCTION_REGISTRY_SERVICE}/functions/{function_id}",
            timeout=5
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Function registry service timeout'}), 504
    except Exception as e:
        logger.error(f"Error getting user function: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-functions/<function_id>', methods=['DELETE'])
def delete_user_function(function_id):
    """Delete a user function"""
    try:
        response = requests.delete(
            f"{FUNCTION_REGISTRY_SERVICE}/functions/{function_id}",
            timeout=5
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Function registry service timeout'}), 504
    except Exception as e:
        logger.error(f"Error deleting user function: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-functions/<function_id>/execute', methods=['POST'])
def execute_user_function(function_id):
    """Execute a user-uploaded function"""
    try:
        data = request.json
        payload = data.get('payload', {})
        
        logger.info(f"Executing user function: {function_id}")
        
        # Forward to scheduler with user function marker
        response = requests.post(
            f"{SCHEDULER_SERVICE}/submit-user-function",
            json={
                'function_id': function_id,
                'payload': payload
            },
            timeout=5
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Scheduler service timeout'}), 504
    except Exception as e:
        logger.error(f"Error executing user function: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-functions/<function_id>/executions', methods=['GET'])
def get_user_function_executions(function_id):
    """Get execution history for a user function"""
    try:
        limit = request.args.get('limit', 50)
        
        response = requests.get(
            f"{FUNCTION_REGISTRY_SERVICE}/functions/{function_id}/executions",
            params={'limit': limit},
            timeout=5
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Function registry service timeout'}), 504
    except Exception as e:
        logger.error(f"Error getting executions: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== HOME/DOCS ====================

@app.route('/', methods=['GET'])
def index():
    """Landing page with API documentation"""
    return '''
    <html>
        <head>
            <title>SOPM - Serverless Operating System Process Manager</title>
            <style>
                body { font-family: Arial; max-width: 1000px; margin: 50px auto; padding: 20px; }
                code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
                pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
                .section { margin: 30px 0; }
                .endpoint { background: #e8f5e9; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .endpoint-new { background: #fff3e0; padding: 15px; margin: 10px 0; border-radius: 5px; }
                h3 { color: #2196F3; }
            </style>
        </head>
        <body>
            <h1>🚀 SOPM API Gateway</h1>
            <p><strong>Serverless Operating System Process Manager</strong> - Zero Cold Start • 100 Functions • User Upload Support</p>
            
            <div class="section">
                <h2>📡 Pre-loaded Functions API</h2>
                
                <div class="endpoint">
                    <strong>GET /api/functions</strong>
                    <p>List all 100 pre-loaded functions</p>
                </div>
                
                <div class="endpoint">
                    <strong>POST /api/execute</strong>
                    <p>Execute a pre-loaded function</p>
                    <pre>
{
  "function_name": "sentiment_analysis",
  "payload": {"text": "I love SOPM!"}
}</pre>
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/status/:job_id</strong>
                    <p>Get job execution status</p>
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/jobs</strong>
                    <p>List recent jobs</p>
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/stats</strong>
                    <p>Get system statistics</p>
                </div>
            </div>
            
            <div class="section">
                <h2>📤 User-Uploaded Functions API (NEW)</h2>
                
                <div class="endpoint-new">
                    <strong>POST /api/user-functions</strong>
                    <p>Upload a new function</p>
                    <pre>
{
  "user_id": "user123",
  "name": "my_function",
  "description": "My custom function",
  "runtime": "python3.11",
  "code": "def handler(event): return {'result': 'success'}",
  "dependencies": "requests==2.31.0",
  "memory_limit_mb": 128,
  "timeout_seconds": 30
}</pre>
                </div>
                
                <div class="endpoint-new">
                    <strong>GET /api/user-functions?user_id=xxx</strong>
                    <p>List your uploaded functions</p>
                </div>
                
                <div class="endpoint-new">
                    <strong>GET /api/user-functions/:function_id</strong>
                    <p>Get function details and build status</p>
                </div>
                
                <div class="endpoint-new">
                    <strong>POST /api/user-functions/:function_id/execute</strong>
                    <p>Execute your uploaded function</p>
                    <pre>
{
  "payload": {"key": "value"}
}</pre>
                </div>
                
                <div class="endpoint-new">
                    <strong>GET /api/user-functions/:function_id/executions</strong>
                    <p>Get execution history</p>
                </div>
                
                <div class="endpoint-new">
                    <strong>DELETE /api/user-functions/:function_id</strong>
                    <p>Delete a function</p>
                </div>
            </div>
            
            <div class="section">
                <h2>⚡ Performance</h2>
                <ul>
                    <li><strong>Pre-loaded Functions:</strong> 0ms cold start, 10-50ms execution</li>
                    <li><strong>User Functions:</strong> 100-200ms cold start (gVisor), 10-50ms warm execution</li>
                    <li><strong>Concurrency:</strong> Unlimited (scales with Kubernetes)</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>🔒 Security</h2>
                <ul>
                    <li>User functions run in <strong>gVisor sandbox</strong></li>
                    <li>Network isolation via NetworkPolicies</li>
                    <li>Resource limits enforced</li>
                    <li>Code validation before build</li>
                </ul>
            </div>
            
            <p style="margin-top: 40px; color: #666;">
                <strong>Note:</strong> User-uploaded functions are built using Kaniko and stored in a private registry.
                Build time: 30-60 seconds. Max code size: 100KB. Allowed packages: requests, pandas, numpy, flask, etc.
            </p>
        </body>
    </html>
    '''

if __name__ == '__main__':
    logger.info("Gateway service starting...")
    app.run(host='0.0.0.0', port=80, debug=False)
