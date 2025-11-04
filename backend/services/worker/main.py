from flask import Flask, request, jsonify
import time
import logging

# Import all function modules
from functions import data_processing, text_analysis, api_integrations, utilities, math_compute

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register all functions at startup (PRE-LOADING = ZERO COLD START!)
FUNCTIONS = {}

def register_functions():
    """Register all available functions"""
    global FUNCTIONS
    
    # ==================== DATA PROCESSING (20 functions) ====================
    FUNCTIONS['csv_parser'] = data_processing.csv_parser
    FUNCTIONS['json_validator'] = data_processing.json_validator
    FUNCTIONS['data_aggregator'] = data_processing.data_aggregator
    FUNCTIONS['data_filter'] = data_processing.data_filter
    FUNCTIONS['data_sorter'] = data_processing.data_sorter
    FUNCTIONS['deduplicator'] = data_processing.deduplicator
    FUNCTIONS['data_merger'] = data_processing.data_merger
    FUNCTIONS['column_renamer'] = data_processing.column_renamer
    FUNCTIONS['missing_value_handler'] = data_processing.missing_value_handler
    FUNCTIONS['data_transpose'] = data_processing.data_transpose
    FUNCTIONS['column_selector'] = data_processing.column_selector
    FUNCTIONS['row_slicer'] = data_processing.row_slicer
    FUNCTIONS['data_groupby'] = data_processing.data_groupby
    FUNCTIONS['csv_to_json'] = data_processing.csv_to_json
    FUNCTIONS['json_to_csv'] = data_processing.json_to_csv
    FUNCTIONS['data_pivot'] = data_processing.data_pivot
    FUNCTIONS['data_describe'] = data_processing.data_describe
    FUNCTIONS['column_dropper'] = data_processing.column_dropper
    FUNCTIONS['data_sampler'] = data_processing.data_sampler
    FUNCTIONS['value_counter'] = data_processing.value_counter
    
    # ==================== TEXT ANALYSIS (20 functions) ====================
    FUNCTIONS['sentiment_analysis'] = text_analysis.sentiment_analysis
    FUNCTIONS['word_counter'] = text_analysis.word_counter
    FUNCTIONS['text_summarizer'] = text_analysis.text_summarizer
    FUNCTIONS['language_detector'] = text_analysis.language_detector
    FUNCTIONS['spam_detector'] = text_analysis.spam_detector
    FUNCTIONS['text_cleaner'] = text_analysis.text_cleaner
    FUNCTIONS['keyword_extractor'] = text_analysis.keyword_extractor
    FUNCTIONS['character_counter'] = text_analysis.character_counter
    FUNCTIONS['text_case_converter'] = text_analysis.text_case_converter
    FUNCTIONS['text_reverser'] = text_analysis.text_reverser
    FUNCTIONS['palindrome_checker'] = text_analysis.palindrome_checker
    FUNCTIONS['vowel_counter'] = text_analysis.vowel_counter
    FUNCTIONS['text_splitter'] = text_analysis.text_splitter
    FUNCTIONS['text_replacer'] = text_analysis.text_replacer
    FUNCTIONS['email_extractor'] = text_analysis.email_extractor
    FUNCTIONS['url_extractor'] = text_analysis.url_extractor
    FUNCTIONS['phone_extractor'] = text_analysis.phone_extractor
    FUNCTIONS['text_truncator'] = text_analysis.text_truncator
    FUNCTIONS['word_replacer'] = text_analysis.word_replacer
    FUNCTIONS['text_diff'] = text_analysis.text_diff
    
    # ==================== MATH/COMPUTE (20 functions) ====================
    FUNCTIONS['prime_checker'] = math_compute.prime_checker
    FUNCTIONS['fibonacci_generator'] = math_compute.fibonacci_generator
    FUNCTIONS['factorial_calculator'] = math_compute.factorial_calculator
    FUNCTIONS['gcd_calculator'] = math_compute.gcd_calculator
    FUNCTIONS['lcm_calculator'] = math_compute.lcm_calculator
    FUNCTIONS['power_calculator'] = math_compute.power_calculator
    FUNCTIONS['square_root_calculator'] = math_compute.square_root_calculator
    FUNCTIONS['logarithm_calculator'] = math_compute.logarithm_calculator
    FUNCTIONS['percentage_calculator'] = math_compute.percentage_calculator
    FUNCTIONS['average_calculator'] = math_compute.average_calculator
    FUNCTIONS['median_calculator'] = math_compute.median_calculator
    FUNCTIONS['mode_calculator'] = math_compute.mode_calculator
    FUNCTIONS['standard_deviation_calculator'] = math_compute.standard_deviation_calculator
    FUNCTIONS['range_calculator'] = math_compute.range_calculator
    FUNCTIONS['combination_calculator'] = math_compute.combination_calculator
    FUNCTIONS['permutation_calculator'] = math_compute.permutation_calculator
    FUNCTIONS['trigonometry_calculator'] = math_compute.trigonometry_calculator
    FUNCTIONS['absolute_value'] = math_compute.absolute_value
    FUNCTIONS['rounding_calculator'] = math_compute.rounding_calculator
    FUNCTIONS['distance_calculator'] = math_compute.distance_calculator
    
    # ==================== API INTEGRATIONS (20 functions) ====================
    FUNCTIONS['weather_fetcher'] = api_integrations.weather_fetcher
    FUNCTIONS['ip_geolocation'] = api_integrations.ip_geolocation
    FUNCTIONS['url_shortener_info'] = api_integrations.url_shortener_info
    FUNCTIONS['random_quote_generator'] = api_integrations.random_quote_generator
    FUNCTIONS['random_user_generator'] = api_integrations.random_user_generator
    FUNCTIONS['cat_fact_fetcher'] = api_integrations.cat_fact_fetcher
    FUNCTIONS['dog_image_fetcher'] = api_integrations.dog_image_fetcher
    FUNCTIONS['joke_generator'] = api_integrations.joke_generator
    FUNCTIONS['advice_generator'] = api_integrations.advice_generator
    FUNCTIONS['github_user_info'] = api_integrations.github_user_info
    FUNCTIONS['cryptocurrency_price'] = api_integrations.cryptocurrency_price
    FUNCTIONS['country_info'] = api_integrations.country_info
    FUNCTIONS['number_facts'] = api_integrations.number_facts
    FUNCTIONS['json_placeholder_post'] = api_integrations.json_placeholder_post
    FUNCTIONS['bored_activity'] = api_integrations.bored_activity
    FUNCTIONS['university_search'] = api_integrations.university_search
    FUNCTIONS['gender_predictor'] = api_integrations.gender_predictor
    FUNCTIONS['age_predictor'] = api_integrations.age_predictor
    FUNCTIONS['nationality_predictor'] = api_integrations.nationality_predictor
    FUNCTIONS['public_ip_fetcher'] = api_integrations.public_ip_fetcher
    
    # ==================== UTILITIES (20 functions) ====================
    FUNCTIONS['hash_generator'] = utilities.hash_generator
    FUNCTIONS['base64_encoder'] = utilities.base64_encoder
    FUNCTIONS['base64_decoder'] = utilities.base64_decoder
    FUNCTIONS['qr_code_generator'] = utilities.qr_code_generator
    FUNCTIONS['password_generator'] = utilities.password_generator
    FUNCTIONS['uuid_generator'] = utilities.uuid_generator
    FUNCTIONS['timestamp_converter'] = utilities.timestamp_converter
    FUNCTIONS['calculator'] = utilities.calculator
    FUNCTIONS['json_formatter'] = utilities.json_formatter
    FUNCTIONS['json_minifier'] = utilities.json_minifier
    FUNCTIONS['hex_to_rgb'] = utilities.hex_to_rgb
    FUNCTIONS['rgb_to_hex'] = utilities.rgb_to_hex
    FUNCTIONS['random_number_generator'] = utilities.random_number_generator
    FUNCTIONS['string_to_binary'] = utilities.string_to_binary
    FUNCTIONS['binary_to_string'] = utilities.binary_to_string
    FUNCTIONS['url_encoder'] = utilities.url_encoder
    FUNCTIONS['url_decoder'] = utilities.url_decoder
    FUNCTIONS['string_sorter'] = utilities.string_sorter
    FUNCTIONS['list_shuffler'] = utilities.list_shuffler
    FUNCTIONS['text_statistics'] = utilities.text_statistics

    logger.info(f"✅ Registered {len(FUNCTIONS)} functions across 5 categories")

# Register all functions on startup
register_functions()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'functions_loaded': len(FUNCTIONS)
    })

@app.route('/execute', methods=['POST'])
def execute():
    """Execute a function"""
    start_time = time.time()
    
    try:
        data = request.json
        function_name = data.get('function_name')
        payload = data.get('payload', {})
        
        if not function_name:
            return jsonify({'error': 'function_name is required'}), 400
        
        if function_name not in FUNCTIONS:
            return jsonify({
                'error': f'Function {function_name} not found',
                'available_functions': list(FUNCTIONS.keys())
            }), 404
        
        # Execute the function
        logger.info(f"⚡ Executing function: {function_name}")
        result = FUNCTIONS[function_name](payload)
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return jsonify({
            'function_name': function_name,
            'result': result,
            'execution_time_ms': round(execution_time, 2)
        })
        
    except Exception as e:
        logger.error(f"❌ Error executing function: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/functions', methods=['GET'])
def list_functions():
    """List all available functions"""
    return jsonify({
        'total_functions': len(FUNCTIONS),
        'functions': list(FUNCTIONS.keys())
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
