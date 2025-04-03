# -*- coding: utf-8 -*-
import sys
import os
from assistant.filesystem import get_directory_structure_with_ignore, create_file, get_latest_file, get_file_content
from assistant.api import call_gemini_api
from assistant.utils import ensure_directory
from assistant.core import get_next_file_number

ASSISTANT_DIR = ".assistant"
API_KEYS = ["GOOGLE_API_KEY"]

def assistant_config():
    """Configura as variáveis de ambiente necessárias."""
    print("Configurando as chaves de API:")
    for key in API_KEYS:
        value = input(f"'{key}': ").strip()
        if value:
            os.environ[key] = value
            print(f"Variável de ambiente '{key}' : '{os.environ[key]}' configurada.")
        else:
            print(f"Atenção: '{key}' não foi configurada.")

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
        print('Uso: assistant start | run | setup | configure')
        sys.exit(1)

    command = sys.argv[1]
    if command == 'start':
        assistant_start()
    elif command == 'run':
        assistant_run()
    elif command == 'setup':
        assistant_setup()
    elif command == 'configure':
        assistant_config()
    else:
        print('Comando inválido. Use start, run ou setup.')

if __name__ == "__main__":
    main()