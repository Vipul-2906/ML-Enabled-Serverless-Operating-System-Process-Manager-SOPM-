from textblob import TextBlob
import re
from collections import Counter
from typing import Dict, Any

def sentiment_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze sentiment of text"""
    try:
        text = payload.get('text', '')
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'success': True,
            'sentiment': sentiment,
            'polarity': polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def word_counter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Count word frequency"""
    try:
        text = payload.get('text', '')
        top_n = payload.get('top_n', 10)
        
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        return {
            'success': True,
            'total_words': len(words),
            'unique_words': len(word_freq),
            'top_words': dict(word_freq.most_common(top_n))
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def text_summarizer(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key sentences (simple summarization)"""
    try:
        text = payload.get('text', '')
        num_sentences = payload.get('num_sentences', 3)
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        summary = '. '.join(sentences[:num_sentences]) + '.'
        
        return {
            'success': True,
            'original_sentences': len(sentences),
            'summary': summary
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def language_detector(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Detect language of text"""
    try:
        text = payload.get('text', '')
        blob = TextBlob(text)
        
        return {
            'success': True,
            'language': blob.detect_language(),
            'confidence': 'high'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def spam_detector(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Simple spam detection based on keywords"""
    try:
        text = payload.get('text', '').lower()
        
        spam_keywords = ['free', 'win', 'winner', 'click here', 'limited time', 
                        'act now', 'prize', 'congratulations', '!!!', 'urgent']
        
        spam_score = sum(keyword in text for keyword in spam_keywords)
        is_spam = spam_score >= 3
        
        return {
            'success': True,
            'is_spam': is_spam,
            'spam_score': spam_score,
            'max_score': len(spam_keywords)
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def text_cleaner(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Clean text by removing special characters, extra spaces, etc."""
    try:
        text = payload.get('text', '')
        
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return {
            'success': True,
            'original_length': len(text),
            'cleaned_length': len(cleaned),
            'cleaned_text': cleaned
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def keyword_extractor(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract important keywords"""
    try:
        text = payload.get('text', '')
        top_n = payload.get('top_n', 5)
        
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 
                     'were', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        keywords = Counter(filtered_words).most_common(top_n)
        
        return {
            'success': True,
            'keywords': [{'word': word, 'frequency': freq} for word, freq in keywords]
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def character_counter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Count characters, words, sentences, paragraphs"""
    try:
        text = payload.get('text', '')
        
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        return {
            'success': True,
            'characters': char_count,
            'characters_no_spaces': char_count_no_spaces,
            'words': word_count,
            'sentences': sentence_count,
            'paragraphs': paragraph_count
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def text_case_converter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert text case"""
    try:
        text = payload.get('text', '')
        case_type = payload.get('case', 'upper')  # upper, lower, title, capitalize
        
        conversions = {
            'upper': text.upper(),
            'lower': text.lower(),
            'title': text.title(),
            'capitalize': text.capitalize()
        }
        
        converted = conversions.get(case_type, text)
        
        return {
            'success': True,
            'original': text,
            'converted': converted,
            'case_type': case_type
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def text_reverser(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Reverse text"""
    try:
        text = payload.get('text', '')
        reversed_text = text[::-1]
        
        return {
            'success': True,
            'original': text,
            'reversed': reversed_text
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def palindrome_checker(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Check if text is a palindrome"""
    try:
        text = payload.get('text', '')
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
        is_palindrome = cleaned == cleaned[::-1]
        
        return {
            'success': True,
            'text': text,
            'is_palindrome': is_palindrome
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def vowel_counter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Count vowels and consonants"""
    try:
        text = payload.get('text', '').lower()
        vowels = 'aeiou'
        
        vowel_count = sum(1 for char in text if char in vowels)
        consonant_count = sum(1 for char in text if char.isalpha() and char not in vowels)
        
        return {
            'success': True,
            'vowels': vowel_count,
            'consonants': consonant_count,
            'total_letters': vowel_count + consonant_count
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def text_splitter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Split text by delimiter"""
    try:
        text = payload.get('text', '')
        delimiter = payload.get('delimiter', ' ')
        
        parts = text.split(delimiter)
        
        return {
            'success': True,
            'parts': parts,
            'count': len(parts)
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def text_replacer(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Replace text"""
    try:
        text = payload.get('text', '')
        find = payload.get('find', '')
        replace = payload.get('replace', '')
        
        replaced = text.replace(find, replace)
        count = text.count(find)
        
        return {
            'success': True,
            'original': text,
            'replaced': replaced,
            'replacements_made': count
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def email_extractor(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract email addresses from text"""
    try:
        text = payload.get('text', '')
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        return {
            'success': True,
            'emails_found': len(emails),
            'emails': emails
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def url_extractor(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract URLs from text"""
    try:
        text = payload.get('text', '')
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        return {
            'success': True,
            'urls_found': len(urls),
            'urls': urls
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def phone_extractor(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract phone numbers from text"""
    try:
        text = payload.get('text', '')
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        
        return {
            'success': True,
            'phones_found': len(phones),
            'phones': phones
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def text_truncator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Truncate text to specified length"""
    try:
        text = payload.get('text', '')
        max_length = payload.get('max_length', 100)
        suffix = payload.get('suffix', '...')
        
        if len(text) <= max_length:
            truncated = text
        else:
            truncated = text[:max_length] + suffix
        
        return {
            'success': True,
            'original_length': len(text),
            'truncated': truncated,
            'was_truncated': len(text) > max_length
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def word_replacer(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Replace specific words"""
    try:
        text = payload.get('text', '')
        replacements = payload.get('replacements', {})
        
        replaced_text = text
        for old_word, new_word in replacements.items():
            replaced_text = re.sub(r'\b' + old_word + r'\b', new_word, replaced_text)
        
        return {
            'success': True,
            'original': text,
            'replaced': replaced_text
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def text_diff(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Find differences between two texts"""
    try:
        text1 = payload.get('text1', '')
        text2 = payload.get('text2', '')
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        only_in_text1 = list(words1 - words2)
        only_in_text2 = list(words2 - words1)
        common = list(words1 & words2)
        
        return {
            'success': True,
            'only_in_text1': only_in_text1,
            'only_in_text2': only_in_text2,
            'common_words': common
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}