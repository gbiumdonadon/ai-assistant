import os
import requests
import glob
from google.api_core.exceptions import GoogleAPIError
from dotenv import load_dotenv

load_dotenv()

def get_directory_structure(path, ignore_files):
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
                with open(filepath, 'r') as file:
                    file_content = file.read()
                    structure += f'\n{subindent}## {filepath} ##\n{file_content}\n\n'
            except FileNotFoundError:
                structure += f'\n{subindent}## {filepath} ##\nArquivo não encontrado\n\n'
            except Exception as e:
                structure += f'\n{subindent}## {filepath} ##\nErro ao ler o arquivo: {e}\n\n'
    return structure


def process_assistant_ignore(base_path, ignore_file_path=".assistantignore"):
    """
    Processa o arquivo .assistantignore e retorna uma lista de paths relativos a serem ignorados,
    """
    ignore_list = []
    try:
        with open(os.path.join(base_path, ignore_file_path), 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Ignora linhas vazias e comentários
                    pattern = os.path.join(base_path, line)
                    for filepath in glob.glob(pattern):
                        ignore_list.append(filepath)
    except FileNotFoundError:
        print(f"Arquivo {base_path}{ignore_file_path} não encontrado. Nenhum arquivo será ignorado.")
    return ignore_list

def get_directory_structure_with_ignore(path):
    """
    Obtém a estrutura de diretórios e conteúdo dos arquivos, aplicando as regras de ignore do .assistantignore.
    """
    ignore_files = process_assistant_ignore(path)
    return get_directory_structure(path, ignore_files)

def get_file_content(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ''

def get_latest_user_file():
    user_files = [f for f in os.listdir('.assistant') if f.startswith('user_') and f.endswith('.md')]
    if not user_files:
        return None
    user_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    return user_files[-1]

def get_latest_assistant_file():
    assistant_files = [f for f in os.listdir('.assistant') if f.startswith('assistant_') and f.endswith('.md')]
    if not assistant_files:
        return None
    assistant_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    return assistant_files[-1]

def get_next_file_number(directory, prefix):
    files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith('.md')]
    if not files:
        return 1
    numbers = [int(f.split('_')[1].split('.')[0]) for f in files]
    return max(numbers) + 1

def assistant_start():
    os.makedirs('.assistant', exist_ok=True)

    structure = get_directory_structure_with_ignore('./')

    with open('.assistant/assistant_01.md', 'w') as assistant_file:
        assistant_file.write(f'### Files ###\n{structure}\n\n')

    latest_user_file = get_latest_user_file()
    if latest_user_file:
        user_number = int(latest_user_file.split('_')[1].split('.')[0]) + 1
    else:
        user_number = 1
    open(f'.assistant/user_{user_number:02d}.md', 'w').close()

def assistant_run():
    api_key = os.getenv('GOOGLE_API_KEY')  # Read from environment variables using os.getenv()

    if not api_key:
        print("Erro: GOOGLE_API_KEY not found in .env file or environment variables.")
        return

    latest_assistant_file = get_latest_assistant_file()
    if not latest_assistant_file:
        print('Erro: Nenhum arquivo assistant_ encontrado.')
        return

    latest_user_file = get_latest_user_file()
    if not latest_user_file:
        print('Erro: Nenhum arquivo user_ encontrado.')
        return

    assistant_content = get_file_content(os.path.join('.assistant', latest_assistant_file))
    user_content = get_file_content(os.path.join('.assistant', latest_user_file))
    concatenated_content = f"`{assistant_content}`{user_content}"  # formata��o melhorada
    print('Prompt enviado:\n' + concatenated_content)

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
    headers = {'Content-Type': 'application/json'}
    data = {
        'system_instruction': {
            'parts': [
                {
                    'text': 'You are a expert developer.'
                }
            ]
        },
        'contents': [{
            'parts': [{'text': concatenated_content}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        generated_text = response_json['candidates'][0]['content']['parts'][0]['text']

        next_assistant_number = get_next_file_number(".assistant", "assistant_")
        with open(f'.assistant/assistant_{next_assistant_number:02d}.md', 'w', encoding='utf-8') as new_assistant_file:
            new_assistant_file.write(generated_text)

        next_user_number = get_next_file_number(".assistant", "user_")
        open(f'.assistant/user_{next_user_number:02d}.md', 'w').close()

    except requests.exceptions.HTTPError as e:
        print(f'Erro HTTP: {e}')
        print(f'Resposta da API: {response.text}') # adicionado para debug
    except requests.exceptions.RequestException as e:
        print(f'Erro na requisi��o: {e}')
    except (KeyError, IndexError) as e:
        print(f'Erro ao processar a resposta da API: {e}')
    except GoogleAPIError as e:
        print(f"Erro da API do Google: {e}")

def assistant_setup():
    return False

if __name__ == '__main__':
    import sys

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
        print('Comando inv�lido. Use start, run ou setup.')
