# 🚀 Guia Rápido de Execução

## Passo 1: Instalar Dependências

Abra um terminal na pasta do projeto e execute:

```bash
# Recomendo usar um ambiente virtual (venv) para isolamento.

# Windows - PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Windows - CMD
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Passo 2: Configurar Variáveis de Ambiente

### Opção A: Usar o script automático
```bash
python setup.py
```

### Opção B: Criar manualmente

Crie um arquivo chamado `.env` na raiz do projeto com o seguinte conteúdo:

```env
# Google OAuth (obrigatório para Google Calendar)
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Gemini API (obrigatório para interpretação de comandos)
GEMINI_API_KEY=sua_chave_gemini_aqui

# Slack (opcional - pode configurar via painel depois)
SLACK_BOT_TOKEN=seu_token_slack_aqui

# Segurança (gerados automaticamente pelo setup.py)
SECRET_KEY=chave_secreta_gerada
ENCRYPTION_KEY=chave_criptografia_gerada
```

### Como obter as credenciais:

#### Google OAuth (Client ID e Secret):
1. Acesse https://console.cloud.google.com/
2. Crie um novo projeto ou selecione um existente
3. Ative a API "Google Calendar API"
4. Vá em "Credenciais" → "Criar credenciais" → "ID do cliente OAuth"
5. Tipo: "Aplicativo da Web"
6. Adicione `http://localhost:8000/auth/google/callback` como URI de redirecionamento
7. Copie o Client ID e Client Secret para o `.env`

#### Gemini API Key:
1. Acesse https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave para `GEMINI_API_KEY` no `.env`

#### Slack Bot Token (opcional):
1. Acesse https://api.slack.com/apps
2. Crie um novo app
3. Vá em "OAuth & Permissions"
4. Adicione scopes: `chat:write`, `channels:read`
5. Instale o app no workspace
6. Copie o "Bot User OAuth Token" para `SLACK_BOT_TOKEN` no `.env` (ou configure depois via painel)

## Passo 3: Executar o Sistema

Você precisa de **2 terminais** abertos:

### Terminal 1 - Backend (API)

**Windows:**
```bash
run_backend.bat
```

**Linux/Mac:**
```bash
chmod +x run_backend.sh
./run_backend.sh
```

**Ou manualmente:**
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Nota: usar `python -m uvicorn` garante que o `uvicorn` instalado no ambiente virtual ativo será executado (evita o erro "'uvicorn' não é reconhecido").

Você deve ver algo como:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Terminal 2 - Frontend (Interface Web)

**Windows:**
```bash
run_frontend.bat
```

**Linux/Mac:**
```bash
chmod +x run_frontend.sh
./run_frontend.sh
```

**Ou manualmente:**
```bash
streamlit run frontend/app.py
```

Você deve ver algo como:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## Passo 4: Acessar a Interface

Abra seu navegador e acesse:
- **Interface Principal**: http://localhost:8501
- **API Backend**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs

## Passo 5: Configurar Ferramentas

### Conectar Google Calendar (OAuth 2.0):

1. Na interface web, vá para "⚙️ Painel de Controle"
2. Na aba "🔐 Conectar Google"
3. Digite seu User ID (ex: "usuario123")
4. Clique em "🔗 Conectar Google"
5. Será aberta uma nova aba com login do Google
6. Faça login e autorize o acesso
7. Você será redirecionado de volta com confirmação

### Configurar Slack (Chave Estática):

1. Na interface web, vá para "⚙️ Painel de Controle"
2. Na aba "🔑 Configurar Chaves"
3. Selecione "slack"
4. Cole seu Bot Token do Slack
5. Clique em "💾 Salvar Chave"

## Passo 6: Usar o Sistema

1. Na interface, vá para "🏠 Executar Comando"
2. Digite seu comando em linguagem natural, por exemplo:
   ```
   Marque uma reunião de alinhamento no meu Google Calendar amanhã às 10h e avise no canal #projetos do Slack
   ```
3. Clique em "🚀 Executar"
4. Aguarde a execução
5. Veja a resposta consolidada!

## ⚠️ Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Erro: "Google OAuth não configurado"
- Verifique se `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` estão no `.env`
- Certifique-se de que o arquivo `.env` está na raiz do projeto

### Erro: "GEMINI_API_KEY não configurada"
- Verifique se `GEMINI_API_KEY` está no `.env`
- Obtenha uma chave em https://makersuite.google.com/app/apikey

### Erro: "Não foi possível conectar ao backend"
- Certifique-se de que o backend está rodando na porta 8000
- Verifique se não há outro processo usando a porta 8000
- Tente acessar http://localhost:8000 diretamente no navegador

### Erro: "Port already in use"
- Feche outros processos usando as portas 8000 ou 8501
- Ou altere as portas nos scripts de execução

### OAuth do Google não funciona
- Verifique se adicionou `http://localhost:8000/auth/google/callback` como URI de redirecionamento no Google Cloud Console
- Certifique-se de que o Client ID e Secret estão corretos no `.env`

## ✅ Checklist de Execução

- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado e configurado
- [ ] Google Client ID e Secret configurados
- [ ] Gemini API Key configurada
- [ ] Backend rodando na porta 8000
- [ ] Frontend rodando na porta 8501
- [ ] Google Calendar conectado via OAuth
- [ ] Slack configurado (opcional)

## 🎉 Pronto!

Agora você pode usar o Gateway Inteligente! Experimente comandos como:

- "Marque uma reunião amanhã às 14h"
- "Crie um evento 'Sprint Planning' hoje às 15h e avise no Slack"
- "Marque reunião no dia 25/01/2024 às 10h"

