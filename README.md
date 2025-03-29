# ai-assistant

# Assistente de Desenvolvedor com Gemini API

Este projeto implementa um assistente de linha de comando que utiliza a API Gemini para auxiliar em tarefas de desenvolvimento.

## Pré-requisitos

* Python 3.6+
* Uma chave de API do Gemini (Google Cloud).

## Instalação

1.  Clone este repositório:

    ```bash
    git clone <URL_DO_REPOSITÓRIO>
    cd <NOME_DO_DIRETÓRIO>
    ```

2.  Instale as dependências:

    ```bash
    pip install requests
    ```

3.  Configure sua chave de API:

    * Você pode inserir sua chave API diretamente no código, alterando a linha:
        `api_key = 'SUA_CHAVE_API'` dentro da função `assistant_run`.
    * Como alternativa, você pode passar a chave de API como um argumento da linha de comando ao executar o comando `run`.

## Uso

O assistente possui os seguintes comandos:

* `start`: Inicia um novo assistente, criando um diretório `.assistant` e um arquivo `assistant_01.md` com a estrutura de diretórios e arquivos do projeto.
* `run`: Executa o assistente, enviando o conteúdo do arquivo `assistant_01.md` e do último arquivo `user_*.md` para a API Gemini e salvando a resposta em um novo arquivo `assistant_*.md`.
* `setup`: Comando reservado para implementações futuras, como configurações e personalizações do assistente.

### Exemplos

1.  Inicie um novo assistente:

    ```bash
    python seu_script.py start
    ```

2.  Execute o assistente:

    ```bash
    python seu_script.py run
    ```
    Caso você não tenha inserido a chave API diretamente no código, você pode passar ela como argumento:
    ```bash
    python seu_script.py run SUA_CHAVE_API
    ```

## Estrutura de Arquivos

* `.assistant/`: Diretório que armazena os arquivos de histórico do assistente.
    * `assistant_*.md`: Arquivos contendo as respostas da API Gemini.
    * `user_*.md`: Arquivos contendo as perguntas/comandos do usuário.
* `.assistantignore`: Arquivo opcional que especifica os diretórios e arquivos a serem ignorados ao gerar a estrutura do projeto.

## Classe GeminiAPI

A classe `GeminiAPI` encapsula a lógica de interação com a API Gemini. Ela possui os seguintes métodos:

* `__init__(api_key)`: Inicializa a classe com a chave da API.
* `generate_content(prompt)`: Envia um prompt para a API Gemini e retorna a resposta.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir pull requests ou relatar problemas.
