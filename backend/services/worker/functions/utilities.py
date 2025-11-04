import hashlib
import base64
import qrcode
import io
from typing import Dict, Any
import random
import string
import json

def hash_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate various hashes for input text"""
    try:
        text = payload.get('text', '')
        
        return {
            'success': True,
            'md5': hashlib.md5(text.encode()).hexdigest(),
            'sha1': hashlib.sha1(text.encode()).hexdigest(),
            'sha256': hashlib.sha256(text.encode()).hexdigest()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def base64_encoder(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Encode text to base64"""
    try:
        text = payload.get('text', '')
        encoded = base64.b64encode(text.encode()).decode()
        
        return {
            'success': True,
            'original': text,
            'encoded': encoded
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def base64_decoder(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Decode base64 text"""
    try:
        encoded = payload.get('encoded', '')
        decoded = base64.b64decode(encoded).decode()
        
        return {
            'success': True,
            'decoded': decoded
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def qr_code_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate QR code (returns base64 encoded image)"""
    try:
        text = payload.get('text', '')
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            'success': True,
            'qr_code_base64': img_str,
            'text': text
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def password_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a random secure password"""
    try:
        length = payload.get('length', 16)
        include_special = payload.get('include_special', True)
        
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += string.punctuation
        
        password = ''.join(random.choice(chars) for _ in range(length))
        
        return {
            'success': True,
            'password': password,
            'length': len(password)
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def uuid_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate UUIDs"""
    try:
        import uuid
        count = payload.get('count', 1)
        
        uuids = [str(uuid.uuid4()) for _ in range(count)]
        
        return {
            'success': True,
            'uuids': uuids,
            'count': len(uuids)
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def timestamp_converter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert between timestamp formats"""
    try:
        from datetime import datetime
        timestamp = payload.get('timestamp', None)
        
        if timestamp:
            dt = datetime.fromtimestamp(int(timestamp))
        else:
            dt = datetime.now()
        
        return {
            'success': True,
            'unix_timestamp': int(dt.timestamp()),
            'iso_format': dt.isoformat(),
            'human_readable': dt.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Perform basic calculations"""
    try:
        operation = payload.get('operation', 'add')
        a = float(payload.get('a', 0))
        b = float(payload.get('b', 0))
        
        operations = {
            'add': a + b,
            'subtract': a - b,
            'multiply': a * b,
            'divide': a / b if b != 0 else 'Error: Division by zero',
            'power': a ** b,
            'modulo': a % b if b != 0 else 'Error: Division by zero'
        }
        
        result = operations.get(operation, 'Invalid operation')
        
        return {
            'success': True,
            'operation': operation,
            'a': a,
            'b': b,
            'result': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def json_formatter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Format JSON with indentation"""
    try:
        json_data = payload.get('json_data', '{}')
        indent = payload.get('indent', 2)
        
        parsed = json.loads(json_data)
        formatted = json.dumps(parsed, indent=indent)
        
        return {
            'success': True,
            'formatted': formatted
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def json_minifier(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Minify JSON (remove whitespace)"""
    try:
        json_data = payload.get('json_data', '{}')
        
        parsed = json.loads(json_data)
        minified = json.dumps(parsed, separators=(',', ':'))
        
        original_size = len(json_data)
        minified_size = len(minified)
        
        return {
            'success': True,
            'minified': minified,
            'original_size': original_size,
            'minified_size': minified_size,
            'savings': original_size - minified_size
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def hex_to_rgb(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert HEX color to RGB"""
    try:
        hex_color = payload.get('hex', '#FFFFFF').lstrip('#')
        
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return {
            'success': True,
            'hex': '#' + hex_color,
            'rgb': {'r': r, 'g': g, 'b': b}
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def rgb_to_hex(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert RGB color to HEX"""
    try:
        r = int(payload.get('r', 255))
        g = int(payload.get('g', 255))
        b = int(payload.get('b', 255))
        
        hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        return {
            'success': True,
            'rgb': {'r': r, 'g': g, 'b': b},
            'hex': hex_color
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def random_number_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate random numbers"""
    try:
        min_val = payload.get('min', 1)
        max_val = payload.get('max', 100)
        count = payload.get('count', 1)
        
        numbers = [random.randint(min_val, max_val) for _ in range(count)]
        
        return {
            'success': True,
            'numbers': numbers,
            'count': len(numbers),
            'min': min_val,
            'max': max_val
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def string_to_binary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert string to binary"""
    try:
        text = payload.get('text', '')
        binary = ' '.join(format(ord(char), '08b') for char in text)
        
        return {
            'success': True,
            'text': text,
            'binary': binary
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def binary_to_string(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert binary to string"""
    try:
        binary = payload.get('binary', '')
        binary_values = binary.split()
        text = ''.join(chr(int(bv, 2)) for bv in binary_values)
        
        return {
            'success': True,
            'binary': binary,
            'text': text
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def url_encoder(payload: Dict[str, Any]) -> Dict[str, Any]:
    """URL encode text"""
    try:
        from urllib.parse import quote
        text = payload.get('text', '')
        encoded = quote(text)
        
        return {
            'success': True,
            'original': text,
            'encoded': encoded
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def url_decoder(payload: Dict[str, Any]) -> Dict[str, Any]:
    """URL decode text"""
    try:
        from urllib.parse import unquote
        encoded = payload.get('encoded', '')
        decoded = unquote(encoded)
        
        return {
            'success': True,
            'encoded': encoded,
            'decoded': decoded
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def string_sorter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Sort strings"""
    try:
        strings = payload.get('strings', [])
        reverse = payload.get('reverse', False)
        
        sorted_strings = sorted(strings, reverse=reverse)
        
        return {
            'success': True,
            'original': strings,
            'sorted': sorted_strings,
            'reverse': reverse
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def list_shuffler(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Shuffle a list"""
    try:
        items = payload.get('items', [])
        shuffled = items.copy()
        random.shuffle(shuffled)
        
        return {
            'success': True,
            'original': items,
            'shuffled': shuffled
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def text_statistics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze text: count words, characters, vowels, consonants"""
    try:
        text = payload.get('text', '')
        vowels = "aeiouAEIOU"
        vowel_count = sum(1 for ch in text if ch in vowels)
        consonant_count = sum(1 for ch in text if ch.isalpha() and ch not in vowels)
        word_count = len(text.split())
        char_count = len(text)

        return {
            'success': True,
            'text': text,
            'words': word_count,
            'characters': char_count,
            'vowels': vowel_count,
            'consonants': consonant_count
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}