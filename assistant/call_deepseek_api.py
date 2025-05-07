import os
import yaml
import logging
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def call_deepseek_api(assistant_content, user_content, model="deepseek-chat"):
    """
    Calls the DeepSeek API and returns the generated text.

    Args:
        assistant_content (str): The assistant's initial content or context.
        user_content (str): The user's input or query.
        model (str, optional): The DeepSeek model to use ("deepseek-chat" or "deepseek-reasoner").
            Defaults to "deepseek-chat".

    Returns:
        str: The generated text from the DeepSeek API, or None on error.
    """
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")

    try:
        config_file = ".assistant/config.yaml"
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            persona = config['system_instruction'][0]
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_file}")
        return None
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        return None
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        return None

    url = 'https://api.deepseek.com/v1/chat/completions'  # Or the appropriate DeepSeek API endpoint.
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        "model": model,  #  "deepseek-chat" or "deepseek-reasoner"
        "messages": [
            {"role": "system", "content": persona},  # Use persona from config
            {"role": "user", "content": f"{assistant_content}{user_content}"}  # Combine inputs
        ],
        "stream": 'false'
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            if 'message' in response_json['choices'][0]:
                return response_json['choices'][0]['message']['content']
            elif 'text' in response_json['choices'][0]:
                return response_json['choices'][0]['text']
        else:
            logging.warning(f"Unexpected response structure from DeepSeek API: {response_json}")
            return None

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error: {e}, Response: {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Error: {e}")
        return None
    except ValueError as e:
        logging.error(f"JSON Decode Error: {e}, Response: {response.text}")
        return None
    except KeyError as e:
        logging.error(f"KeyError: {e}, Response: {response_json}")
        return None