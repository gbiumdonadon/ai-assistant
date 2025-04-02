import sys
import os
from assistant.io import (get_directory_structure_with_ignore, create_file,
                          get_latest_file, get_file_content)
from assistant.api import call_gemini_api
from assistant.utils import ensure_directory
from assistant.core import get_next_file_number


ASSISTANT_DIR = ".assistant"

def assistant_start():
    """Initializes the assistant."""
    ensure_directory(ASSISTANT_DIR)
    structure = get_directory_structure_with_ignore('./')
    create_file(f"{ASSISTANT_DIR}/assistant_01.md", f'### Files ###\n{structure}\n\n')
    create_file(f"{ASSISTANT_DIR}/user_01.md")


def assistant_run():
    """Runs the main assistant loop."""
    latest_assistant_file = get_latest_file(ASSISTANT_DIR, "assistant_")
    latest_user_file = get_latest_file(ASSISTANT_DIR, "user_")

    if not latest_assistant_file or not latest_user_file:
        print("Error: No assistant or user file found.")
        return

    assistant_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_assistant_file))
    print(assistant_content)
    user_content = get_file_content(os.path.join(ASSISTANT_DIR, latest_user_file))

    # print('Prompt enviado:\n' + f"`{assistant_content}`{user_content}")

    try:
        generated_text = call_gemini_api(assistant_content, user_content)
        next_assistant_number = get_next_file_number(ASSISTANT_DIR, "assistant_")
        create_file(f"{ASSISTANT_DIR}/assistant_{next_assistant_number:02d}.md", generated_text)
        next_user_number = get_next_file_number(ASSISTANT_DIR, "user_")
        create_file(f"{ASSISTANT_DIR}/user_{next_user_number:02d}.md")
    except RuntimeError as e:
        print(f"Error: {e}")


def assistant_setup():
    """Performs any setup actions (currently does nothing)."""
    return False


if __name__ == '__main__':
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