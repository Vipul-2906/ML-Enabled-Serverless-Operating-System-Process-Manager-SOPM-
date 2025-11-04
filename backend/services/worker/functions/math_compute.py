import math
from typing import Dict, Any, List

def prime_checker(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Check if number is prime"""
    try:
        n = int(payload.get('number', 2))
        
        if n < 2:
            is_prime = False
        elif n == 2:
            is_prime = True
        elif n % 2 == 0:
            is_prime = False
        else:
            is_prime = all(n % i != 0 for i in range(3, int(math.sqrt(n)) + 1, 2))
        
        return {
            'success': True,
            'number': n,
            'is_prime': is_prime
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def fibonacci_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Fibonacci sequence"""
    try:
        n = int(payload.get('count', 10))
        
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[-1] + fib[-2])
        
        return {
            'success': True,
            'count': n,
            'sequence': fib[:n]
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def factorial_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate factorial"""
    try:
        n = int(payload.get('number', 5))
        
        if n < 0:
            return {'success': False, 'error': 'Factorial not defined for negative numbers'}
        
        result = math.factorial(n)
        
        return {
            'success': True,
            'number': n,
            'factorial': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def gcd_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate GCD of two numbers"""
    try:
        a = int(payload.get('a', 12))
        b = int(payload.get('b', 18))
        
        result = math.gcd(a, b)
        
        return {
            'success': True,
            'a': a,
            'b': b,
            'gcd': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def lcm_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate LCM of two numbers"""
    try:
        a = int(payload.get('a', 12))
        b = int(payload.get('b', 18))
        
        result = abs(a * b) // math.gcd(a, b)
        
        return {
            'success': True,
            'a': a,
            'b': b,
            'lcm': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def power_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate power"""
    try:
        base = float(payload.get('base', 2))
        exponent = float(payload.get('exponent', 3))
        
        result = base ** exponent
        
        return {
            'success': True,
            'base': base,
            'exponent': exponent,
            'result': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def square_root_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate square root"""
    try:
        number = float(payload.get('number', 16))
        
        if number < 0:
            return {'success': False, 'error': 'Cannot calculate square root of negative number'}
        
        result = math.sqrt(number)
        
        return {
            'success': True,
            'number': number,
            'square_root': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def logarithm_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate logarithm"""
    try:
        number = float(payload.get('number', 100))
        base = float(payload.get('base', 10))
        
        if number <= 0 or base <= 0 or base == 1:
            return {'success': False, 'error': 'Invalid input for logarithm'}
        
        result = math.log(number, base)
        
        return {
            'success': True,
            'number': number,
            'base': base,
            'logarithm': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def percentage_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate percentage"""
    try:
        value = float(payload.get('value', 50))
        total = float(payload.get('total', 200))
        
        if total == 0:
            return {'success': False, 'error': 'Total cannot be zero'}
        
        percentage = (value / total) * 100
        
        return {
            'success': True,
            'value': value,
            'total': total,
            'percentage': percentage
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def average_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate average of numbers"""
    try:
        numbers = payload.get('numbers', [])
        
        if not numbers:
            return {'success': False, 'error': 'No numbers provided'}
        
        avg = sum(numbers) / len(numbers)
        
        return {
            'success': True,
            'count': len(numbers),
            'sum': sum(numbers),
            'average': avg
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def median_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate median of numbers"""
    try:
        numbers = sorted(payload.get('numbers', []))
        
        if not numbers:
            return {'success': False, 'error': 'No numbers provided'}
        
        n = len(numbers)
        if n % 2 == 0:
            median = (numbers[n//2 - 1] + numbers[n//2]) / 2
        else:
            median = numbers[n//2]
        
        return {
            'success': True,
            'count': n,
            'median': median
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def mode_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate mode of numbers"""
    try:
        numbers = payload.get('numbers', [])
        
        if not numbers:
            return {'success': False, 'error': 'No numbers provided'}
        
        from collections import Counter
        count = Counter(numbers)
        max_count = max(count.values())
        mode = [num for num, freq in count.items() if freq == max_count]
        
        return {
            'success': True,
            'mode': mode,
            'frequency': max_count
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def standard_deviation_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate standard deviation"""
    try:
        numbers = payload.get('numbers', [])
        
        if not numbers:
            return {'success': False, 'error': 'No numbers provided'}
        
        mean = sum(numbers) / len(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
        std_dev = math.sqrt(variance)
        
        return {
            'success': True,
            'count': len(numbers),
            'mean': mean,
            'variance': variance,
            'standard_deviation': std_dev
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def range_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate range of numbers"""
    try:
        numbers = payload.get('numbers', [])
        
        if not numbers:
            return {'success': False, 'error': 'No numbers provided'}
        
        min_val = min(numbers)
        max_val = max(numbers)
        range_val = max_val - min_val
        
        return {
            'success': True,
            'min': min_val,
            'max': max_val,
            'range': range_val
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def combination_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate combination nCr"""
    try:
        n = int(payload.get('n', 5))
        r = int(payload.get('r', 2))
        
        if n < 0 or r < 0 or r > n:
            return {'success': False, 'error': 'Invalid input for combination'}
        
        result = math.comb(n, r)
        
        return {
            'success': True,
            'n': n,
            'r': r,
            'combination': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def permutation_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate permutation nPr"""
    try:
        n = int(payload.get('n', 5))
        r = int(payload.get('r', 2))
        
        if n < 0 or r < 0 or r > n:
            return {'success': False, 'error': 'Invalid input for permutation'}
        
        result = math.perm(n, r)
        
        return {
            'success': True,
            'n': n,
            'r': r,
            'permutation': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def trigonometry_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate trigonometric functions"""
    try:
        angle = float(payload.get('angle', 45))
        unit = payload.get('unit', 'degrees')  # degrees or radians
        
        if unit == 'degrees':
            angle_rad = math.radians(angle)
        else:
            angle_rad = angle
        
        return {
            'success': True,
            'angle': angle,
            'unit': unit,
            'sin': math.sin(angle_rad),
            'cos': math.cos(angle_rad),
            'tan': math.tan(angle_rad)
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def absolute_value(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate absolute value"""
    try:
        number = float(payload.get('number', -42))
        result = abs(number)
        
        return {
            'success': True,
            'number': number,
            'absolute_value': result
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def rounding_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Round number to specified decimal places"""
    try:
        number = float(payload.get('number', 3.14159))
        decimals = int(payload.get('decimals', 2))
        
        rounded = round(number, decimals)
        floor_val = math.floor(number)
        ceil_val = math.ceil(number)
        
        return {
            'success': True,
            'original': number,
            'rounded': rounded,
            'floor': floor_val,
            'ceil': ceil_val
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def distance_calculator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate distance between two points"""
    try:
        x1 = float(payload.get('x1', 0))
        y1 = float(payload.get('y1', 0))
        x2 = float(payload.get('x2', 3))
        y2 = float(payload.get('y2', 4))
        
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        return {
            'success': True,
            'point1': (x1, y1),
            'point2': (x2, y2),
            'distance': distance
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}