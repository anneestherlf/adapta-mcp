# ADAPTA MCP Gateway
Case Inteli Academy + ADAPTA

<img align="center" src="/frontend/static/adapta-logo.png">

Sistema de gateway unificado que traduz comandos em linguagem natural em ações executadas em múltiplas APIs, com gerenciamento centralizado de segurança e autenticação.

## Arquitetura

O sistema é composto por 6 componentes principais:

1. **Painel de Controle** (Passo 0): Configuração de ferramentas e credenciais
2. **Interface de Apresentação** (Passo 1): Interface web para entrada de comandos
3. **Gateway Unificado** (Passo 2): Backend único que recebe todas as requisições
4. **Roteamento Inteligente** (Passo 3): LLM que interpreta comandos e decide ações
5. **Hub de MCPs** (Passo 4): Adaptadores para cada ferramenta/API
6. **Cofre de Chaves** (Passo 5): Gerenciamento centralizado de credenciais
7. **Consolidação de Respostas** (Passo 6): Agregação e formatação de respostas

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Execute o script de setup:
```bash
python setup.py
```

Ou crie manualmente o arquivo `.env` com as seguintes variáveis:

- `GOOGLE_CLIENT_ID`: ID do cliente OAuth do Google (obtenha em [Google Cloud Console](https://console.cloud.google.com/))
- `GOOGLE_CLIENT_SECRET`: Secret do cliente OAuth do Google
- `GOOGLE_REDIRECT_URI`: URI de redirecionamento (padrão: `http://localhost:8000/auth/google/callback`)
- `GEMINI_API_KEY`: Chave da API do Google Gemini (obtenha em [Google AI Studio](https://makersuite.google.com/app/apikey))
- `SLACK_BOT_TOKEN`: Token do bot do Slack (opcional, pode ser configurado via painel)
- `SECRET_KEY`: Chave secreta gerada automaticamente
- `ENCRYPTION_KEY`: Chave de criptografia gerada automaticamente

### 3. Configurar Google OAuth

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a API do Google Calendar
4. Configure a tela de consentimento OAuth
5. Crie credenciais OAuth 2.0 (tipo "Aplicativo da Web")
6. Adicione `http://localhost:8000/auth/google/callback` como URI de redirecionamento autorizado.
   - Para desenvolvimento local com TLS (recomendado): você pode gerar um certificado autoassinado e usar `https://localhost:8000/auth/google/callback` como URI de redirecionamento autorizado.
   - O repositório inclui um gerador de certificado em `tools/generate_self_signed_cert.py` e os scripts `run_backend.bat` / `run_backend.sh` foram atualizados para iniciar o backend com TLS automaticamente quando os certificados existirem.
7. Copie o Client ID e Client Secret para o arquivo `.env`

## Execução

### Windows
```bash
# Terminal 1 - Backend
run_backend.bat

# Terminal 2 - Frontend
run_frontend.bat
```

### Linux/Mac
```bash
# Terminal 1 - Backend
chmod +x run_backend.sh
./run_backend.sh

# Terminal 2 - Frontend
chmod +x run_frontend.sh
./run_frontend.sh
```

### Manual
```bash
# Terminal 1 - Backend (sem TLS)
uvicorn backend.main:app --reload --port 8000

# Terminal 1 - Backend (com TLS usando certificados em `certs/`)
# Gere certificados com: `python tools/generate_self_signed_cert.py`
uvicorn backend.main:app --reload --port 8000 --ssl-certfile certs/cert.pem --ssl-keyfile certs/key.pem

# Terminal 2 - Frontend
streamlit run frontend/app.py
```

### Acessos
- **Frontend (Interface)**: http://localhost:8501
- **Backend (API)**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs

## Uso

### Passo a Passo

1. **Inicie os servidores** (backend e frontend)

2. **Configure as credenciais**:
   - Acesse o Painel de Controle na interface web
   - Conecte sua conta Google (OAuth 2.0) - Tipo A
   - Configure chaves de API estáticas (Slack, etc.) - Tipo B

3. **Execute comandos**:
   - Vá para a página "Executar Comando"
   - Digite seu comando em linguagem natural
   - O sistema interpreta, executa e retorna resposta consolidada

### Fluxo de Autenticação

**Tipo A (OAuth 2.0 - Google Calendar)**:
1. Usuário clica em "Conectar Google" no Painel de Controle
2. É redirecionado para tela de login do Google
3. Autoriza o acesso
4. Sistema recebe `refresh_token` e armazena no Cofre
5. Quando necessário, usa `refresh_token` para obter `access_token` temporário

**Tipo B (Chave Estática - Slack)**:
1. Administrador insere chave de API no Painel de Controle
2. Chave é armazenada no Cofre (criptografada)
3. Quando necessário, chave é recuperada e usada diretamente

## Exemplo

**Comando:**
```
Marque uma 'Reunião de Alinhamento' no meu Google Calendar amanhã às 10h e avise no canal #projetos do Slack que a reunião foi marcada.
```

**Resultado:**
- Evento criado no Google Calendar
- Mensagem enviada no Slack
- Resposta consolidada: "Pronto! Marquei a 'Reunião de Alinhamento' no seu Google Calendar e avisei o canal #projetos no Slack."

