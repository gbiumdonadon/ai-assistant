# -*- coding: utf-8 -*- 
import os
import requests
from google.api_core.exceptions import GoogleAPIError
from dotenv import load_dotenv
from assistant.core import process_assistant_response

load_dotenv(dotenv_path='../')

def call_gemini_api(assistant_content, user_content):
    """Calls the Gemini API and returns the generated text."""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
    headers = {'Content-Type': 'application/json'}
    data = {
        'system_instruction': {
            'parts': [{'text': 'You are an expert developer.'}]
        },
        'contents': [{'parts': [{'text': f"`{assistant_content}`{user_content}"}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=data, params={'key': api_key})
        response.raise_for_status()
        return process_assistant_response(response.json())
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP Error: {e}, Response: {response.text}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request Error: {e}") from e
    except ValueError as e:
        raise RuntimeError(f"API Response Error: {e}") from e
    except GoogleAPIError as e:
        raise RuntimeError(f"Google API Error: {e}") from e