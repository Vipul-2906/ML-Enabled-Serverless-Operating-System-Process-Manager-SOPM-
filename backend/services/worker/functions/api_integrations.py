import requests
from typing import Dict, Any
import time
import random

def weather_fetcher(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch weather data for a city"""
    try:
        city = payload.get('city', 'London')
        response = requests.get(f'https://wttr.in/{city}?format=j1', timeout=5)
        
        if response.ok:
            data = response.json()
            current = data['current_condition'][0]
            return {
                'success': True,
                'city': city,
                'temperature_c': current['temp_C'],
                'temperature_f': current['temp_F'],
                'condition': current['weatherDesc'][0]['value'],
                'humidity': current['humidity'],
                'wind_speed_kmph': current['windspeedKmph']
            }
        else:
            return {'success': False, 'error': 'Failed to fetch weather'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def ip_geolocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get geolocation info for an IP address"""
    try:
        ip = payload.get('ip', '')
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'ip': data.get('query'),
                'country': data.get('country'),
                'region': data.get('regionName'),
                'city': data.get('city'),
                'timezone': data.get('timezone'),
                'isp': data.get('isp')
            }
        else:
            return {'success': False, 'error': 'Failed to fetch geolocation'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def url_shortener_info(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get info about a URL (mock - returns metadata)"""
    try:
        url = payload.get('url', '')
        import hashlib
        short_code = hashlib.md5(url.encode()).hexdigest()[:6]
        
        return {
            'success': True,
            'original_url': url,
            'short_code': short_code,
            'short_url': f'https://short.link/{short_code}'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def random_quote_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get a random inspirational quote"""
    try:
        response = requests.get('https://api.quotable.io/random', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'quote': data['content'],
                'author': data['author'],
                'tags': data['tags']
            }
        else:
            return {'success': False, 'error': 'Failed to fetch quote'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def random_user_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate random user data"""
    try:
        response = requests.get('https://randomuser.me/api/', timeout=5)
        
        if response.ok:
            data = response.json()['results'][0]
            return {
                'success': True,
                'name': f"{data['name']['first']} {data['name']['last']}",
                'email': data['email'],
                'username': data['login']['username'],
                'country': data['location']['country'],
                'phone': data['phone']
            }
        else:
            return {'success': False, 'error': 'Failed to generate user'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def cat_fact_fetcher(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get a random cat fact"""
    try:
        response = requests.get('https://catfact.ninja/fact', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'fact': data['fact'],
                'length': data['length']
            }
        else:
            return {'success': False, 'error': 'Failed to fetch cat fact'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def dog_image_fetcher(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get a random dog image URL"""
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'image_url': data['message'],
                'status': data['status']
            }
        else:
            return {'success': False, 'error': 'Failed to fetch dog image'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def joke_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get a random joke"""
    try:
        response = requests.get('https://official-joke-api.appspot.com/random_joke', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'type': data['type'],
                'setup': data['setup'],
                'punchline': data['punchline']
            }
        else:
            return {'success': False, 'error': 'Failed to fetch joke'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def advice_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get random advice"""
    try:
        response = requests.get('https://api.adviceslip.com/advice', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'advice': data['slip']['advice'],
                'id': data['slip']['id']
            }
        else:
            return {'success': False, 'error': 'Failed to fetch advice'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def github_user_info(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get GitHub user information"""
    try:
        username = payload.get('username', 'torvalds')
        response = requests.get(f'https://api.github.com/users/{username}', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'username': data['login'],
                'name': data.get('name'),
                'bio': data.get('bio'),
                'public_repos': data['public_repos'],
                'followers': data['followers'],
                'following': data['following']
            }
        else:
            return {'success': False, 'error': 'User not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def cryptocurrency_price(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get cryptocurrency price"""
    try:
        crypto = payload.get('crypto', 'bitcoin').lower()
        currency = payload.get('currency', 'usd').lower()
        
        response = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies={currency}',
            timeout=5
        )
        
        if response.ok:
            data = response.json()
            if crypto in data:
                return {
                    'success': True,
                    'crypto': crypto,
                    'currency': currency,
                    'price': data[crypto][currency]
                }
            else:
                return {'success': False, 'error': 'Cryptocurrency not found'}
        else:
            return {'success': False, 'error': 'Failed to fetch price'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def country_info(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get country information"""
    try:
        country = payload.get('country', 'usa')
        response = requests.get(f'https://restcountries.com/v3.1/alpha/{country}', timeout=5)
        
        if response.ok:
            data = response.json()[0]
            return {
                'success': True,
                'name': data['name']['common'],
                'capital': data.get('capital', ['N/A'])[0],
                'population': data.get('population'),
                'region': data.get('region'),
                'currency': list(data.get('currencies', {}).keys())
            }
        else:
            return {'success': False, 'error': 'Country not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def number_facts(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get interesting facts about a number"""
    try:
        number = payload.get('number', 42)
        response = requests.get(f'http://numbersapi.com/{number}', timeout=5)
        
        if response.ok:
            return {
                'success': True,
                'number': number,
                'fact': response.text
            }
        else:
            return {'success': False, 'error': 'Failed to fetch fact'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def json_placeholder_post(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get sample post from JSONPlaceholder"""
    try:
        post_id = payload.get('post_id', 1)
        response = requests.get(f'https://jsonplaceholder.typicode.com/posts/{post_id}', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'id': data['id'],
                'title': data['title'],
                'body': data['body'],
                'userId': data['userId']
            }
        else:
            return {'success': False, 'error': 'Failed to fetch post'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def bored_activity(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get a random activity suggestion"""
    try:
        response = requests.get('https://www.boredapi.com/api/activity', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'activity': data['activity'],
                'type': data['type'],
                'participants': data['participants'],
                'price': data['price']
            }
        else:
            return {'success': False, 'error': 'Failed to fetch activity'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def university_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Search for universities by country"""
    try:
        country = payload.get('country', 'United States')
        response = requests.get(
            f'http://universities.hipolabs.com/search?country={country}',
            timeout=5
        )
        
        if response.ok:
            data = response.json()[:5]  # Return first 5
            universities = [{
                'name': uni['name'],
                'website': uni['web_pages'][0] if uni['web_pages'] else 'N/A'
            } for uni in data]
            
            return {
                'success': True,
                'country': country,
                'count': len(universities),
                'universities': universities
            }
        else:
            return {'success': False, 'error': 'Failed to fetch universities'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def gender_predictor(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Predict gender from name"""
    try:
        name = payload.get('name', 'John')
        response = requests.get(f'https://api.genderize.io?name={name}', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'name': data['name'],
                'gender': data.get('gender', 'unknown'),
                'probability': data.get('probability', 0)
            }
        else:
            return {'success': False, 'error': 'Failed to predict gender'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def age_predictor(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Predict age from name"""
    try:
        name = payload.get('name', 'John')
        response = requests.get(f'https://api.agify.io?name={name}', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'name': data['name'],
                'age': data.get('age', 'unknown'),
                'count': data.get('count', 0)
            }
        else:
            return {'success': False, 'error': 'Failed to predict age'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def nationality_predictor(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Predict nationality from name"""
    try:
        name = payload.get('name', 'John')
        response = requests.get(f'https://api.nationalize.io?name={name}', timeout=5)
        
        if response.ok:
            data = response.json()
            countries = data.get('country', [])[:3]  # Top 3
            
            return {
                'success': True,
                'name': data['name'],
                'predictions': [{
                    'country_id': c['country_id'],
                    'probability': c['probability']
                } for c in countries]
            }
        else:
            return {'success': False, 'error': 'Failed to predict nationality'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def public_ip_fetcher(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Get public IP address"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        
        if response.ok:
            data = response.json()
            return {
                'success': True,
                'ip': data['ip']
            }
        else:
            return {'success': False, 'error': 'Failed to fetch IP'}
    except Exception as e:
        return {'success': False, 'error': str(e)}