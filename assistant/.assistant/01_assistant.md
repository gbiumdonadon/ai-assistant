######### Files ######### 
/
    api.py

    ## ./api.py ##
# -*- coding: utf-8 -*- 
import os
import requests
from google.api_core.exceptions import GoogleAPIError
from dotenv import load_dotenv
from assistant.core import process_assistant_response

load_dotenv()

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

    core.py

    ## ./core.py ##
# -*- coding: utf-8 -*-
import os

def get_next_file_number(directory, prefix):
    """Gets the next available file number for a given prefix."""
    files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
    if not files:
        return 1
    numbers = [int(f.split('_')[0].split('.')[0]) for f in files]
    return max(numbers) + 1

def process_assistant_response(response_json):
    """Safely extracts generated text from the API response."""
    try:
        return response_json['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Could not process API response: {e}") from e

    io.py

    ## ./io.py ##
# -*- coding: utf-8 -*-
import os
import glob
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_directory_structure(path, ignore_files):
    """Generates a string representation of the directory structure."""
    structure = ''
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_files]
        files = [f for f in files if os.path.join(root, f) not in ignore_files]
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            filepath = os.path.join(root, f)
            structure += '{}{}\n'.format(subindent, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    structure += f'\n{subindent}## {filepath} ##\n{file_content}\n\n'
            except FileNotFoundError:
                logging.warning(f"File not found: {filepath}")
                structure += f'\n{subindent}## {filepath} ##\nFile not found\n\n'
            except Exception as e:
                logging.error(f"Error reading file {filepath}: {e}")
                structure += f'\n{subindent}## {filepath} ##\nError reading file: {e}\n\n'
    return structure


def process_assistant_ignore(base_path, ignore_file_path=".assistantignore"):
    """Processes the .assistantignore file, handling relative and absolute paths correctly."""
    ignore_list = []
    ignore_file = Path(base_path) / ignore_file_path
    if ignore_file.exists():
        logging.info(f"Processing ignore file: {ignore_file}")
        try:
            with ignore_file.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Correctly handle relative and absolute paths in .assistantignore
                        ## TODO: Adicionar condição para validar se é um diretório, caso seja deve apenas adicionar o caminho do diretório
                        pattern = os.path.abspath(os.path.join(base_path, line))

                        logging.debug(f"Ignore pattern (absolute): {pattern}")

                        # Use glob.glob with a proper escape for special characters in filenames
                        for filepath in glob.glob(escape_glob_pattern(pattern)):
                            ignore_list.append(filepath)
                            logging.debug(f"Added to ignore list: {filepath}")
        except Exception as e:
            logging.error(f"Error reading .assistantignore file: {e}")
    else:
        logging.info(f"File {ignore_file} not found. No files will be ignored.")
    return ignore_list

def escape_glob_pattern(pattern):
    """Escapes special characters in a glob pattern to prevent unexpected behavior."""
    special_chars = r"[*?[]{}()"
    escaped_pattern = ''.join(c if c not in special_chars else '\\' + c for c in pattern)
    return escaped_pattern


def get_directory_structure_with_ignore(path):
    """Gets the directory structure, applying ignore rules."""
    ignore_files = process_assistant_ignore(path)
    logging.info(f"Files to ignore: {ignore_files}")
    return get_directory_structure(path, ignore_files)

def get_file_content(filepath):
    """Reads the content of a file, returning an empty string if the file doesn't exist."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.warning(f"File not found: {filepath}")
        return ""
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
        return ""

def create_file(filepath, content=""):
    """Creates a file with the given content."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"File created: {filepath}")
    except Exception as e:
        logging.error(f"Error creating file {filepath}: {e}")

def get_latest_file(directory, prefix):
  """Gets the latest file matching a prefix in a directory."""
  files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
  if not files:
      return None
  files.sort(key=lambda x: int(x.split('_')[0].split('.')[0]))
  latest_file = files[-1]
  logging.info(f"Latest file found: {latest_file}")
  return latest_file

    main.py

    ## ./main.py ##
# -*- coding: utf-8 -*-
import sys
import os
from assistant.io import get_directory_structure_with_ignore, create_file, get_latest_file, get_file_content
from assistant.api import call_gemini_api
from assistant.utils import ensure_directory
from assistant.core import get_next_file_number


ASSISTANT_DIR = ".assistant"

def assistant_start():
    """Initializes the assistant."""
    ensure_directory(ASSISTANT_DIR)
    structure = get_directory_structure_with_ignore('./')
    create_file(f"{ASSISTANT_DIR}/01_assistant.md", f'######### Files ######### \n{structure}\n\n')
    create_file(f"{ASSISTANT_DIR}/01_user.md")


def assistant_run():
    """Runs the main assistant loop."""
    latest_assistant_file = get_latest_file(ASSISTANT_DIR, "_assistant")
    latest_user_file = get_latest_file(ASSISTANT_DIR, "_user")

    if not latest_assistant_file or not latest_user_file:
        print("Error: No assistant or user file found.")
        return

    assistant_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_assistant_file))
    user_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_user_file))

    # print('Prompt enviado:\n' + f"`{assistant_content}`{user_content}")

    try:
        generated_text = call_gemini_api(assistant_content, user_content)
        next_assistant_number = get_next_file_number(ASSISTANT_DIR, "_assistant")
        create_file(f"{ASSISTANT_DIR}/{next_assistant_number:02d}_assistant.md", generated_text)
        next_user_number = get_next_file_number(ASSISTANT_DIR, "_user")
        create_file(f"{ASSISTANT_DIR}/{next_user_number:02d}_user.md")
    except RuntimeError as e:
        print(f"Error: {e}")


def assistant_setup():
    """Performs any setup actions (currently does nothing)."""
    return False

def main():
    if len(sys.argv) < 2:
        print('Uso: assistant start | run | setup')
        sys.exit(1)

    command = sys.argv[1]
    if command == 'start':
        assistant_start()
    elif command == 'run':
        assistant_run()
    elif command == 'setup':
        assistant_setup()
    else:
        print('Comando inválido. Use start, run ou setup.')

if __name__ == "__main__":
    main()

    utils.py

    ## ./utils.py ##
# -*- coding: utf-8 -*- 
import os

def ensure_directory(path):
    """Creates a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

    __init__.py

    ## ./__init__.py ##


.assistant/
    01_assistant.md

    ## ./.assistant\01_assistant.md ##
######### Files ######### 
/
    api.py

    ## ./api.py ##
# -*- coding: utf-8 -*- 
import os
import requests
from google.api_core.exceptions import GoogleAPIError
from dotenv import load_dotenv
from assistant.core import process_assistant_response

load_dotenv()

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

    core.py

    ## ./core.py ##
# -*- coding: utf-8 -*-
import os

def get_next_file_number(directory, prefix):
    """Gets the next available file number for a given prefix."""
    files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
    if not files:
        return 1
    numbers = [int(f.split('_')[0].split('.')[0]) for f in files]
    return max(numbers) + 1

def process_assistant_response(response_json):
    """Safely extracts generated text from the API response."""
    try:
        return response_json['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Could not process API response: {e}") from e

    io.py

    ## ./io.py ##
# -*- coding: utf-8 -*-
import os
import glob
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_directory_structure(path, ignore_files):
    """Generates a string representation of the directory structure."""
    structure = ''
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_files]
        files = [f for f in files if os.path.join(root, f) not in ignore_files]
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            filepath = os.path.join(root, f)
            structure += '{}{}\n'.format(subindent, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    structure += f'\n{subindent}## {filepath} ##\n{file_content}\n\n'
            except FileNotFoundError:
                logging.warning(f"File not found: {filepath}")
                structure += f'\n{subindent}## {filepath} ##\nFile not found\n\n'
            except Exception as e:
                logging.error(f"Error reading file {filepath}: {e}")
                structure += f'\n{subindent}## {filepath} ##\nError reading file: {e}\n\n'
    return structure


def process_assistant_ignore(base_path, ignore_file_path=".assistantignore"):
    """Processes the .assistantignore file, handling relative and absolute paths correctly."""
    ignore_list = []
    ignore_file = Path(base_path) / ignore_file_path
    if ignore_file.exists():
        logging.info(f"Processing ignore file: {ignore_file}")
        try:
            with ignore_file.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Correctly handle relative and absolute paths in .assistantignore
                        ## TODO: Adicionar condição para validar se é um diretório, caso seja deve apenas adicionar o caminho do diretório
                        pattern = os.path.abspath(os.path.join(base_path, line))

                        logging.debug(f"Ignore pattern (absolute): {pattern}")

                        # Use glob.glob with a proper escape for special characters in filenames
                        for filepath in glob.glob(escape_glob_pattern(pattern)):
                            ignore_list.append(filepath)
                            logging.debug(f"Added to ignore list: {filepath}")
        except Exception as e:
            logging.error(f"Error reading .assistantignore file: {e}")
    else:
        logging.info(f"File {ignore_file} not found. No files will be ignored.")
    return ignore_list

def escape_glob_pattern(pattern):
    """Escapes special characters in a glob pattern to prevent unexpected behavior."""
    special_chars = r"[*?[]{}()"
    escaped_pattern = ''.join(c if c not in special_chars else '\\' + c for c in pattern)
    return escaped_pattern


def get_directory_structure_with_ignore(path):
    """Gets the directory structure, applying ignore rules."""
    ignore_files = process_assistant_ignore(path)
    logging.info(f"Files to ignore: {ignore_files}")
    return get_directory_structure(path, ignore_files)

def get_file_content(filepath):
    """Reads the content of a file, returning an empty string if the file doesn't exist."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.warning(f"File not found: {filepath}")
        return ""
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
        return ""

def create_file(filepath, content=""):
    """Creates a file with the given content."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"File created: {filepath}")
    except Exception as e:
        logging.error(f"Error creating file {filepath}: {e}")

def get_latest_file(directory, prefix):
  """Gets the latest file matching a prefix in a directory."""
  files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
  if not files:
      return None
  files.sort(key=lambda x: int(x.split('_')[0].split('.')[0]))
  latest_file = files[-1]
  logging.info(f"Latest file found: {latest_file}")
  return latest_file

    main.py

    ## ./main.py ##
# -*- coding: utf-8 -*-
import sys
import os
from assistant.io import get_directory_structure_with_ignore, create_file, get_latest_file, get_file_content
from assistant.api import call_gemini_api
from assistant.utils import ensure_directory
from assistant.core import get_next_file_number


ASSISTANT_DIR = ".assistant"

def assistant_start():
    """Initializes the assistant."""
    ensure_directory(ASSISTANT_DIR)
    structure = get_directory_structure_with_ignore('./')
    create_file(f"{ASSISTANT_DIR}/01_assistant.md", f'######### Files ######### \n{structure}\n\n')
    create_file(f"{ASSISTANT_DIR}/01_user.md")


def assistant_run():
    """Runs the main assistant loop."""
    latest_assistant_file = get_latest_file(ASSISTANT_DIR, "_assistant")
    latest_user_file = get_latest_file(ASSISTANT_DIR, "_user")

    if not latest_assistant_file or not latest_user_file:
        print("Error: No assistant or user file found.")
        return

    assistant_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_assistant_file))
    user_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_user_file))

    # print('Prompt enviado:\n' + f"`{assistant_content}`{user_content}")

    try:
        generated_text = call_gemini_api(assistant_content, user_content)
        next_assistant_number = get_next_file_number(ASSISTANT_DIR, "_assistant")
        create_file(f"{ASSISTANT_DIR}/{next_assistant_number:02d}_assistant.md", generated_text)
        next_user_number = get_next_file_number(ASSISTANT_DIR, "_user")
        create_file(f"{ASSISTANT_DIR}/{next_user_number:02d}_user.md")
    except RuntimeError as e:
        print(f"Error: {e}")


def assistant_setup():
    """Performs any setup actions (currently does nothing)."""
    return False

def main():
    if len(sys.argv) < 2:
        print('Uso: assistant start | run | setup')
        sys.exit(1)

    command = sys.argv[1]
    if command == 'start':
        assistant_start()
    elif command == 'run':
        assistant_run()
    elif command == 'setup':
        assistant_setup()
    else:
        print('Comando inválido. Use start, run ou setup.')

if __name__ == "__main__":
    main()

    utils.py

    ## ./utils.py ##
# -*- coding: utf-8 -*- 
import os

def ensure_directory(path):
    """Creates a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

    __init__.py

    ## ./__init__.py ##


.assistant/
    01_assistant.md

    ## ./.assistant\01_assistant.md ##
######### Files ######### 
/
    api.py

    ## ./api.py ##
# -*- coding: utf-8 -*- 
import os
import requests
from google.api_core.exceptions import GoogleAPIError
from dotenv import load_dotenv
from assistant.core import process_assistant_response

load_dotenv()

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

    core.py

    ## ./core.py ##
# -*- coding: utf-8 -*-
import os

def get_next_file_number(directory, prefix):
    """Gets the next available file number for a given prefix."""
    files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
    if not files:
        return 1
    numbers = [int(f.split('_')[0].split('.')[0]) for f in files]
    return max(numbers) + 1

def process_assistant_response(response_json):
    """Safely extracts generated text from the API response."""
    try:
        return response_json['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Could not process API response: {e}") from e

    io.py

    ## ./io.py ##
# -*- coding: utf-8 -*-
import os
import glob
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_directory_structure(path, ignore_files):
    """Generates a string representation of the directory structure."""
    structure = ''
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_files]
        files = [f for f in files if os.path.join(root, f) not in ignore_files]
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            filepath = os.path.join(root, f)
            structure += '{}{}\n'.format(subindent, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    structure += f'\n{subindent}## {filepath} ##\n{file_content}\n\n'
            except FileNotFoundError:
                logging.warning(f"File not found: {filepath}")
                structure += f'\n{subindent}## {filepath} ##\nFile not found\n\n'
            except Exception as e:
                logging.error(f"Error reading file {filepath}: {e}")
                structure += f'\n{subindent}## {filepath} ##\nError reading file: {e}\n\n'
    return structure


def process_assistant_ignore(base_path, ignore_file_path=".assistantignore"):
    """Processes the .assistantignore file, handling relative and absolute paths correctly."""
    ignore_list = []
    ignore_file = Path(base_path) / ignore_file_path
    if ignore_file.exists():
        logging.info(f"Processing ignore file: {ignore_file}")
        try:
            with ignore_file.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Correctly handle relative and absolute paths in .assistantignore
                        ## TODO: Adicionar condição para validar se é um diretório, caso seja deve apenas adicionar o caminho do diretório
                        pattern = os.path.abspath(os.path.join(base_path, line))

                        logging.debug(f"Ignore pattern (absolute): {pattern}")

                        # Use glob.glob with a proper escape for special characters in filenames
                        for filepath in glob.glob(escape_glob_pattern(pattern)):
                            ignore_list.append(filepath)
                            logging.debug(f"Added to ignore list: {filepath}")
        except Exception as e:
            logging.error(f"Error reading .assistantignore file: {e}")
    else:
        logging.info(f"File {ignore_file} not found. No files will be ignored.")
    return ignore_list

def escape_glob_pattern(pattern):
    """Escapes special characters in a glob pattern to prevent unexpected behavior."""
    special_chars = r"[*?[]{}()"
    escaped_pattern = ''.join(c if c not in special_chars else '\\' + c for c in pattern)
    return escaped_pattern


def get_directory_structure_with_ignore(path):
    """Gets the directory structure, applying ignore rules."""
    ignore_files = process_assistant_ignore(path)
    logging.info(f"Files to ignore: {ignore_files}")
    return get_directory_structure(path, ignore_files)

def get_file_content(filepath):
    """Reads the content of a file, returning an empty string if the file doesn't exist."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.warning(f"File not found: {filepath}")
        return ""
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
        return ""

def create_file(filepath, content=""):
    """Creates a file with the given content."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"File created: {filepath}")
    except Exception as e:
        logging.error(f"Error creating file {filepath}: {e}")

def get_latest_file(directory, prefix):
  """Gets the latest file matching a prefix in a directory."""
  files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
  if not files:
      return None
  files.sort(key=lambda x: int(x.split('_')[0].split('.')[0]))
  latest_file = files[-1]
  logging.info(f"Latest file found: {latest_file}")
  return latest_file

    main.py

    ## ./main.py ##
# -*- coding: utf-8 -*-
import sys
import os
from assistant.io import get_directory_structure_with_ignore, create_file, get_latest_file, get_file_content
from assistant.api import call_gemini_api
from assistant.utils import ensure_directory
from assistant.core import get_next_file_number


ASSISTANT_DIR = ".assistant"

def assistant_start():
    """Initializes the assistant."""
    ensure_directory(ASSISTANT_DIR)
    structure = get_directory_structure_with_ignore('./')
    create_file(f"{ASSISTANT_DIR}/01_assistant.md", f'######### Files ######### \n{structure}\n\n')
    create_file(f"{ASSISTANT_DIR}/01_user.md")


def assistant_run():
    """Runs the main assistant loop."""
    latest_assistant_file = get_latest_file(ASSISTANT_DIR, "_assistant")
    latest_user_file = get_latest_file(ASSISTANT_DIR, "_user")

    if not latest_assistant_file or not latest_user_file:
        print("Error: No assistant or user file found.")
        return

    assistant_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_assistant_file))
    user_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_user_file))

    # print('Prompt enviado:\n' + f"`{assistant_content}`{user_content}")

    try:
        generated_text = call_gemini_api(assistant_content, user_content)
        next_assistant_number = get_next_file_number(ASSISTANT_DIR, "_assistant")
        create_file(f"{ASSISTANT_DIR}/{next_assistant_number:02d}_assistant.md", generated_text)
        next_user_number = get_next_file_number(ASSISTANT_DIR, "_user")
        create_file(f"{ASSISTANT_DIR}/{next_user_number:02d}_user.md")
    except RuntimeError as e:
        print(f"Error: {e}")


def assistant_setup():
    """Performs any setup actions (currently does nothing)."""
    return False

def main():
    if len(sys.argv) < 2:
        print('Uso: assistant start | run | setup')
        sys.exit(1)

    command = sys.argv[1]
    if command == 'start':
        assistant_start()
    elif command == 'run':
        assistant_run()
    elif command == 'setup':
        assistant_setup()
    else:
        print('Comando inválido. Use start, run ou setup.')

if __name__ == "__main__":
    main()

    utils.py

    ## ./utils.py ##
# -*- coding: utf-8 -*- 
import os

def ensure_directory(path):
    """Creates a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

    __init__.py

    ## ./__init__.py ##


.assistant/
    01_assistant.md

    ## ./.assistant\01_assistant.md ##
######### Files ######### 
/
    api.py

    ## ./api.py ##
# -*- coding: utf-8 -*- 
import os
import requests
from google.api_core.exceptions import GoogleAPIError
from dotenv import load_dotenv
from assistant.core import process_assistant_response

load_dotenv()

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

    core.py

    ## ./core.py ##
# -*- coding: utf-8 -*-
import os

def get_next_file_number(directory, prefix):
    """Gets the next available file number for a given prefix."""
    files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
    if not files:
        return 1
    numbers = [int(f.split('_')[0].split('.')[0]) for f in files]
    return max(numbers) + 1

def process_assistant_response(response_json):
    """Safely extracts generated text from the API response."""
    try:
        return response_json['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Could not process API response: {e}") from e

    io.py

    ## ./io.py ##
# -*- coding: utf-8 -*-
import os
import glob
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_directory_structure(path, ignore_files):
    """Generates a string representation of the directory structure."""
    structure = ''
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_files]
        files = [f for f in files if os.path.join(root, f) not in ignore_files]
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            filepath = os.path.join(root, f)
            structure += '{}{}\n'.format(subindent, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    structure += f'\n{subindent}## {filepath} ##\n{file_content}\n\n'
            except FileNotFoundError:
                logging.warning(f"File not found: {filepath}")
                structure += f'\n{subindent}## {filepath} ##\nFile not found\n\n'
            except Exception as e:
                logging.error(f"Error reading file {filepath}: {e}")
                structure += f'\n{subindent}## {filepath} ##\nError reading file: {e}\n\n'
    return structure


def process_assistant_ignore(base_path, ignore_file_path=".assistantignore"):
    """Processes the .assistantignore file, handling relative and absolute paths correctly."""
    ignore_list = []
    ignore_file = Path(base_path) / ignore_file_path
    if ignore_file.exists():
        logging.info(f"Processing ignore file: {ignore_file}")
        try:
            with ignore_file.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Correctly handle relative and absolute paths in .assistantignore
                        ## TODO: Adicionar condição para validar se é um diretório, caso seja deve apenas adicionar o caminho do diretório
                        pattern = os.path.abspath(os.path.join(base_path, line))

                        logging.debug(f"Ignore pattern (absolute): {pattern}")

                        # Use glob.glob with a proper escape for special characters in filenames
                        for filepath in glob.glob(escape_glob_pattern(pattern)):
                            ignore_list.append(filepath)
                            logging.debug(f"Added to ignore list: {filepath}")
        except Exception as e:
            logging.error(f"Error reading .assistantignore file: {e}")
    else:
        logging.info(f"File {ignore_file} not found. No files will be ignored.")
    return ignore_list

def escape_glob_pattern(pattern):
    """Escapes special characters in a glob pattern to prevent unexpected behavior."""
    special_chars = r"[*?[]{}()"
    escaped_pattern = ''.join(c if c not in special_chars else '\\' + c for c in pattern)
    return escaped_pattern


def get_directory_structure_with_ignore(path):
    """Gets the directory structure, applying ignore rules."""
    ignore_files = process_assistant_ignore(path)
    logging.info(f"Files to ignore: {ignore_files}")
    return get_directory_structure(path, ignore_files)

def get_file_content(filepath):
    """Reads the content of a file, returning an empty string if the file doesn't exist."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.warning(f"File not found: {filepath}")
        return ""
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
        return ""

def create_file(filepath, content=""):
    """Creates a file with the given content."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"File created: {filepath}")
    except Exception as e:
        logging.error(f"Error creating file {filepath}: {e}")

def get_latest_file(directory, prefix):
  """Gets the latest file matching a prefix in a directory."""
  files = [f for f in os.listdir(directory) if f.endswith(prefix + '.md')]
  if not files:
      return None
  files.sort(key=lambda x: int(x.split('_')[0].split('.')[0]))
  latest_file = files[-1]
  logging.info(f"Latest file found: {latest_file}")
  return latest_file

    main.py

    ## ./main.py ##
# -*- coding: utf-8 -*-
import sys
import os
from assistant.io import get_directory_structure_with_ignore, create_file, get_latest_file, get_file_content
from assistant.api import call_gemini_api
from assistant.utils import ensure_directory
from assistant.core import get_next_file_number


ASSISTANT_DIR = ".assistant"

def assistant_start():
    """Initializes the assistant."""
    ensure_directory(ASSISTANT_DIR)
    structure = get_directory_structure_with_ignore('./')
    create_file(f"{ASSISTANT_DIR}/01_assistant.md", f'######### Files ######### \n{structure}\n\n')
    create_file(f"{ASSISTANT_DIR}/01_user.md")


def assistant_run():
    """Runs the main assistant loop."""
    latest_assistant_file = get_latest_file(ASSISTANT_DIR, "_assistant")
    latest_user_file = get_latest_file(ASSISTANT_DIR, "_user")

    if not latest_assistant_file or not latest_user_file:
        print("Error: No assistant or user file found.")
        return

    assistant_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_assistant_file))
    user_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_user_file))

    # print('Prompt enviado:\n' + f"`{assistant_content}`{user_content}")

    try:
        generated_text = call_gemini_api(assistant_content, user_content)
        next_assistant_number = get_next_file_number(ASSISTANT_DIR, "_assistant")
        create_file(f"{ASSISTANT_DIR}/{next_assistant_number:02d}_assistant.md", generated_text)
        next_user_number = get_next_file_number(ASSISTANT_DIR, "_user")
        create_file(f"{ASSISTANT_DIR}/{next_user_number:02d}_user.md")
    except RuntimeError as e:
        print(f"Error: {e}")


def assistant_setup():
    """Performs any setup actions (currently does nothing)."""
    return False

def main():
    if len(sys.argv) < 2:
        print('Uso: assistant start | run | setup')
        sys.exit(1)

    command = sys.argv[1]
    if command == 'start':
        assistant_start()
    elif command == 'run':
        assistant_run()
    elif command == 'setup':
        assistant_setup()
    else:
        print('Comando inválido. Use start, run ou setup.')

if __name__ == "__main__":
    main()

    utils.py

    ## ./utils.py ##
# -*- coding: utf-8 -*- 
import os

def ensure_directory(path):
    """Creates a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

    __init__.py

    ## ./__init__.py ##


.assistant/
__pycache__/
    api.cpython-313.pyc

    ## ./__pycache__\api.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    core.cpython-313.pyc

    ## ./__pycache__\core.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    io.cpython-313.pyc

    ## ./__pycache__\io.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    main.cpython-313.pyc

    ## ./__pycache__\main.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    utils.cpython-313.pyc

    ## ./__pycache__\utils.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    __init__.cpython-313.pyc

    ## ./__pycache__\__init__.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte





    01_user.md

    ## ./.assistant\01_user.md ##


__pycache__/
    api.cpython-313.pyc

    ## ./__pycache__\api.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    core.cpython-313.pyc

    ## ./__pycache__\core.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    io.cpython-313.pyc

    ## ./__pycache__\io.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    main.cpython-313.pyc

    ## ./__pycache__\main.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    utils.cpython-313.pyc

    ## ./__pycache__\utils.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    __init__.cpython-313.pyc

    ## ./__pycache__\__init__.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte





    01_user.md

    ## ./.assistant\01_user.md ##


__pycache__/
    api.cpython-313.pyc

    ## ./__pycache__\api.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    core.cpython-313.pyc

    ## ./__pycache__\core.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    io.cpython-313.pyc

    ## ./__pycache__\io.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    main.cpython-313.pyc

    ## ./__pycache__\main.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    utils.cpython-313.pyc

    ## ./__pycache__\utils.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    __init__.cpython-313.pyc

    ## ./__pycache__\__init__.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte





    01_user.md

    ## ./.assistant\01_user.md ##


__pycache__/
    api.cpython-313.pyc

    ## ./__pycache__\api.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    core.cpython-313.pyc

    ## ./__pycache__\core.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    io.cpython-313.pyc

    ## ./__pycache__\io.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    main.cpython-313.pyc

    ## ./__pycache__\main.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    utils.cpython-313.pyc

    ## ./__pycache__\utils.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte

    __init__.cpython-313.pyc

    ## ./__pycache__\__init__.cpython-313.pyc ##
Error reading file: 'utf-8' codec can't decode byte 0xf3 in position 0: invalid continuation byte



