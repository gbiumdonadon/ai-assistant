## Documentação do Assistente de IA

Este documento descreve como instalar e configurar o projeto do Assistente de IA, que utiliza a API do Google Gemini para gerar texto.

**Pré-requisitos:**

* Python 3.7 ou superior.
* Uma conta do Google Cloud com acesso à API do Google Gemini.


**1. Instalando o projeto e suas dependências:**

1. **Clone o repositório.**

2. **Crie um ambiente virtual (Recomendado):**

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate  # Windows
```

**Observação:** Se o arquivo `requirements.txt` não existir, você precisará editar o arquivo `setup.py` e adicionar as dependências necessárias na lista `install_requires`.  No mínimo, você precisará adicionar `requests` e `google-api-core` e `python-dotenv`.  Execute então:


```bash
pip install -e .
```


**2. Configurando o arquivo `.env`:**

O arquivo `.env` contém as variáveis de ambiente necessárias para o funcionamento do projeto.  Crie um arquivo chamado `.env` na raiz do projeto e adicione a seguinte linha, substituindo `<sua_chave_de_api>` pela sua chave de API do Google Gemini:

```
GOOGLE_API_KEY=<sua_chave_de_api>
```

**Obtendo uma chave de API para o Google Gemini:**

Para obter uma chave de API do Google Gemini, siga as etapas descritas na [documentação oficial do Google Cloud](https://cloud.google.com/docs/authentication/getting-started).  Você precisará criar um projeto no Google Cloud Console, habilitar a API do Google Gemini e criar uma chave de API.  Certifique-se de restringir o acesso à sua chave de API o máximo possível para fins de segurança.


**3. Executando o Assistente:**

Depois de instalar as dependências e configurar o arquivo `.env`, você pode executar o assistente usando os seguintes comandos:

* **`assistant start`:** Inicializa o assistente, criando os arquivos iniciais.
* **`assistant run`:** Executa o loop principal do assistente, processando o conteúdo dos arquivos `.md` e gerando uma resposta usando a API do Gemini.  Os arquivos devem ser nomeados segundo o padrão `XX_assistant.md` e `XX_user.md` onde XX é o número sequencial.
* **`assistant setup`:**  (Atualmente sem função)


**Exemplo de Uso:**

```bash
assistant start
assistant run
```

**Observações importantes:**

* O projeto utiliza o arquivo `.assistantignore` para especificar arquivos e diretórios que devem ser ignorados durante a geração da estrutura de diretórios. Adicione os caminhos que você quer ignorar, um por linha neste arquivo.
* A saída do assistente é salva em novos arquivos `.md` na pasta `.assistant`.
* Certifique-se de ter uma conexão estável com a internet, pois o projeto depende de chamadas à API do Google Gemini.
* O tratamento de erros está incluído, mas erros inesperados podem ocorrer.  Verifique a saída do console para obter informações adicionais sobre erros.
* O código inclui várias funções auxiliares para manipulação de arquivos e diretórios.
* O código utiliza a codificação UTF-8. Certifique-se que todos os seus arquivos estejam utilizando esta codificação.  O erro de codificação relatado no código indica arquivos com codificação incorreta que precisam ser corrigidos ou recriados.