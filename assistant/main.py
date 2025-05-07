# -*- coding: utf-8 -*-
import sys
import os
import yaml
from assistant.filesystem import get_directory_structure_with_ignore, create_file, get_latest_file, get_file_content
from assistant.call_gemini_api import call_gemini_api
from assistant.call_deepseek_api import call_deepseek_api
from assistant.call_chatgpt_api import call_chatgpt_api
from assistant.utils import ensure_directory
from assistant.core import get_next_file_number

ASSISTANT_DIR = ".assistant"

def assistant_start():
    """Initializes the assistant."""
    ensure_directory(ASSISTANT_DIR)
    config_file_path = os.path.join(ASSISTANT_DIR, "config.yaml")
    
    # Create config.yaml if it doesn't exist with proper error handling.
    if not os.path.exists(config_file_path):
        config_data = {'system_instruction': [{'persona': "You are an expert developer."}]}
        try:
            with open(config_file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            print(f"Created config file: {config_file_path}")
        except Exception as e:
            print(f"Error creating config file: {e}")
            return
    
    # Create .assistantignore file if it doesn't exist
    ignore_file_path = ".assistantignore"
    if not os.path.exists(ignore_file_path):
        try:
            with open(ignore_file_path, 'w', encoding='utf-8') as f:
                f.write(".assistant\n")
            print(f"Created .assistantignore file")
        except Exception as e:
            print(f"Error creating .assistantignore file: {e}")
            return
        
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

    assistant_content = get_file_content(os.path.join(ASSISTANT_DIR, "01_assistant.md"))
    user_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_user_file))

    try:
        try:
            config_file = ".assistant/config.yaml"
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
                model = config['system_instruction'][1]
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_file}")
            return None

        if model['model'] == 'gemini':
            generated_text = call_gemini_api(assistant_content, user_content)
        elif model['model'] == 'deepseek':
            generated_text = call_deepseek_api(assistant_content, user_content)
        elif model['model'] == 'chatgpt':
            generated_text = call_chatgpt_api(assistant_content, user_content)
        else:
            raise ValueError(f"Model {model} not supported.")

        next_assistant_number = get_next_file_number(ASSISTANT_DIR, "_assistant")
        create_file(f"{ASSISTANT_DIR}/{next_assistant_number:02d}_assistant.md", generated_text)
        next_user_number = get_next_file_number(ASSISTANT_DIR, "_user")
        create_file(f"{ASSISTANT_DIR}/{next_user_number:02d}_user.md")
    except RuntimeError as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) < 2:
        print('Uso: assistant start | run')
        sys.exit(1)

    command = sys.argv[1]
    if command == 'start' or command == 'reset':
        assistant_start()
    elif command == 'run':
        assistant_run()
    else:
        print('Comando inválido. Use start/reset ou run.')

if __name__ == "__main__":
    main()