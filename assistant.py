import os
import requests

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

def assistant_start():
    os.makedirs('.assistant', exist_ok=True)
    ignore_files = []
    if os.path.exists('.assistantignore'):
        with open('.assistantignore', 'r') as ignore_file:
            ignore_files = [os.path.abspath(line.strip()) for line in ignore_file.readlines()]

    structure = get_directory_structure('.', ignore_files)
    with open('.assistant/assistant_01.md', 'w') as assistant_file:
        assistant_file.write(f'### Files ###\n{structure}\n\n')

    latest_user_file = get_latest_user_file()
    if latest_user_file:
        user_number = int(latest_user_file.split('_')[1].split('.')[0]) + 1
    else:
        user_number = 1
    open(f'.assistant/user_{user_number:02d}.md', 'w').close()

def assistant_run(api_key):
    latest_assistant_file = get_latest_assistant_file()
    if not latest_assistant_file:
        print('Erro: Nenhum arquivo assistant_ encontrado.')
        return

    latest_user_file = get_latest_user_file()
    if not latest_user_file:
        print('Erro: Nenhum arquivo user_ encontrado.')
        return

    assistant_content = get_file_content(os.path.join('.assistant/assistant_01.md'))
    user_content = get_file_content('.assistant/' + latest_user_file)
    concatenated_content = '`' + assistant_content + '`' + user_content
    print('Prompt enviado: \n' + concatenated_content)

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
        response.raise_for_status()  # Lança uma exceção para erros HTTP
        response_json = response.json()
        generated_text = response_json['candidates'][0]['content']['parts'][0]['text']

        assistant_number = int(latest_assistant_file.split('_')[1].split('.')[0]) + 1
        with open(f'.assistant/assistant_{assistant_number:02d}.md', 'w') as new_assistant_file:
            new_assistant_file.write(generated_text)

        user_number = int(latest_user_file.split('_')[1].split('.')[0]) + 1
        open(f'.assistant/user_{user_number:02d}.md', 'w').close()

    except requests.exceptions.RequestException as e:
        print(f'Erro na requisição: {e}')
    except (KeyError, IndexError) as e:
        print(f'Erro ao processar a resposta da API: {e}')

def assistant_setup():
    return false

if __name__ == '__main__':
    import sys

    command = sys.argv[1]
    if command == 'start':
        assistant_start()
    elif command == 'run':
        # if len(sys.argv) < 3:
        #     print('Uso: assistant run <API_KEY>')
        #     sys.exit(1)
        # api_key = sys.argv[2]
        api_key = 'AIzaSyBI-uUuoVnTAGjQzK8FiYU8UmU1W76KraQ'
        assistant_run(api_key)
    elif command == 'setup':
        assistant_setup()
    # else:
    #     print('Comando inválido. Use 'start' ou 'run'.')