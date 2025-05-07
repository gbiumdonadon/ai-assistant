import os
import yaml
import logging
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../')

# Configurar o registo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def call_chatgpt_api(assistant_content, user_content, model="gpt-3.5-turbo"):
    """
    Chama a API do ChatGPT e retorna o texto gerado.

    Args:
        assistant_content (str): O conteúdo ou contexto inicial do assistente.
        user_content (str): A entrada ou consulta do utilizador.
        model (str, opcional): O modelo do ChatGPT a usar (e.g., "gpt-4.1", "gpt-4").
            Por padrão é "gpt-4.1".

    Returns:
        str: O texto gerado pela API do ChatGPT, ou None em caso de erro.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrado nas variáveis de ambiente.")

    try:
        config_file = ".assistant/config.yaml"  # Pode ser necessário ajustar este caminho
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            persona = config['system_instruction'][0] # Assumindo que a instrução do sistema está no mesmo lugar.
    except FileNotFoundError:
        logging.error(f"Ficheiro de configuração não encontrado: {config_file}")
        return None
    except yaml.YAMLError as e:
        logging.error(f"Erro ao analisar o ficheiro YAML: {e}")
        return None
    except Exception as e:
        logging.exception(f"Ocorreu um erro inesperado: {e}")
        return None

    url = 'https://api.openai.com/v1/chat/completions'  # Endpoint da API do ChatGPT
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": persona},  # Usar persona da configuração
            {"role": "user", "content": f"{assistant_content}{user_content}"}  # Combinar entradas
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()

        # Extrair o texto da resposta da API do ChatGPT
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['content']
        else:
            logging.warning(f"Estrutura de resposta inesperada da API do ChatGPT: {response_json}")
            return None

    except requests.exceptions.HTTPError as e:
        logging.error(f"Erro HTTP: {e}, Resposta: {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de Requisição: {e}")
        return None
    except ValueError as e:
        logging.error(f"Erro de Decodificação JSON: {e}, Resposta: {response.text}")
        return None
    except KeyError as e:
        logging.error(f"Erro de Chave: {e}, Resposta: {response_json}")
        return None

if __name__ == '__main__':
    # Exemplo de uso:
    assistant_text = "És um assistente útil. Por favor, responde à pergunta do utilizador."
    user_text = "Qual é a capital de França?"
    try:
        chatgpt_response = call_chatgpt_api(assistant_text, user_text)
        if chatgpt_response:
            print(f"Resposta do ChatGPT: {chatgpt_response}")
        else:
            print("Falha ao obter resposta da API do ChatGPT.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
