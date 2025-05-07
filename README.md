## Documentação do Assistente de IA

Este documento descreve como instalar e configurar o projeto do Assistente de IA, que utiliza a API do Google Gemini para gerar texto.

**Pré-requisitos:**

* Python 3.7 ou superior.
* Uma chave de API para a LLM que deseja utilizar (Gemini, ChatGPT, DeepSeek)


**1. Instalando o projeto e suas dependências:**

1. **Clone o repositório.**

2. **Instale a aplicação:**

Execute então:


```bash
pip install -e .
```

**2. Obtendo uma chave de API:**
***2.1 Google Gemini***

Para obter uma chave de API do Google Gemini, siga as etapas descritas na [documentação oficial do Google Cloud](https://cloud.google.com/docs/authentication/getting-started).  Você precisará criar um projeto no Google Cloud Console, habilitar a API do Google Gemini e criar uma chave de API.  Certifique-se de restringir o acesso à sua chave de API o máximo possível para fins de segurança.

***2.1 ChatGPT***
Para obter uma chave de API do ChatGPT, siga estas etapas:

1. Acesse [OpenAI Platform](https://platform.openai.com/api-keys)
2. Clique em "Create new secret key"
3. Crie uma variável de ambiente com o nome OPENAI_API_KEY e o valor de ua API key.




**3. Configure uma variável de ambiente de usuário:**

Configure sua chave de API para as seguintes LLMs:

```
GOOGLE_API_KEY=<sua_chave_de_api>
OPENAI_API_KEY=<sua_chave_de_api>
DEEPSEEK_API_KEY=<sua_chave_de_api>
```

Feche todos os terminais.


**3. Executando o Assistente:**

Depois de instalar as dependências e configurar a variável de ambiente, você pode executar o assistente usando os seguintes comandos:

* **`assistant start`:** Inicializa o assistente, criando os arquivos iniciais.
* **`assistant run`:** Executa o loop principal do assistente, processando o conteúdo dos arquivos `.md` e gerando uma resposta usando a API do Gemini.  Os arquivos devem ser nomeados segundo o padrão `XX_assistant.md` e `XX_user.md` onde XX é o número sequencial.

Utilize do arquivo .assistantignore para especificar arquivos e diretórios que você quer que o assistente desconsidere.


**Exemplo de Uso:**

```bash
ai_assistant start
ai_assistant run
```

**Observações importantes:**

* O projeto utiliza o arquivo `.assistantignore` para especificar arquivos e diretórios que devem ser ignorados durante a geração da estrutura de diretórios. Adicione os caminhos que você quer ignorar, um por linha neste arquivo.
* A saída do assistente é salva em novos arquivos `.md` na pasta `.assistant`.
* O tratamento de erros está incluído, mas erros inesperados podem ocorrer.  Verifique a saída do console para obter informações adicionais sobre erros.