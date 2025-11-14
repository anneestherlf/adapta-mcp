# Exemplos de Uso

## Exemplo 1: Criar Evento no Google Calendar

**Comando:**
```
Marque uma reunião de alinhamento no meu Google Calendar amanhã às 14h
```

**O que acontece:**
1. Sistema identifica necessidade de usar `google_calendar`
2. Extrai parâmetros: título="reunião de alinhamento", data="amanhã", hora="14h"
3. Calcula data real (ex: 2024-01-16T14:00:00)
4. Solicita access_token do Cofre (usa refresh_token do usuário)
5. Cria evento no Google Calendar
6. Retorna: "Pronto! Marquei a 'reunião de alinhamento' no seu Google Calendar para amanhã às 14h."

## Exemplo 2: Criar Evento e Notificar no Slack

**Comando:**
```
Marque uma 'Reunião de Alinhamento' no meu Google Calendar amanhã às 10h e avise no canal #projetos do Slack que a reunião foi marcada.
```

**O que acontece:**
1. Sistema identifica necessidade de usar `google_calendar` E `slack`
2. Gera ExecutionPlan com 2 ações:
   - Ação 1: `google_calendar` com parâmetros do evento
   - Ação 2: `slack` com canal e mensagem
3. Executa ambas as ações em paralelo (ou sequencialmente)
4. Consolida respostas
5. Retorna: "Pronto! Marquei a 'Reunião de Alinhamento' no seu Google Calendar e avisei o canal #projetos no Slack."

## Exemplo 3: Múltiplas Ações

**Comando:**
```
Crie um evento chamado 'Sprint Planning' hoje às 15h no meu calendário, envie uma mensagem no Slack no canal #dev dizendo 'Sprint Planning marcado para hoje às 15h', e depois crie outro evento 'Daily Standup' para amanhã às 9h
```

**O que acontece:**
1. Sistema identifica 3 ações:
   - Criar evento "Sprint Planning" (hoje 15h)
   - Enviar mensagem no Slack
   - Criar evento "Daily Standup" (amanhã 9h)
2. Executa todas as ações
3. Consolida todas as respostas
4. Retorna resumo de todas as ações executadas

## Configuração Inicial

### Passo 1: Configurar Google OAuth

1. Acesse o Painel de Controle na interface web
2. Vá para a aba "Conectar Google"
3. Digite seu User ID (ex: "usuario123")
4. Clique em "Conectar Google"
5. Será redirecionado para login do Google
6. Autorize o acesso
7. Você será redirecionado de volta com confirmação

### Passo 2: Configurar Slack

1. Acesse o Painel de Controle
2. Vá para a aba "Configurar Chaves"
3. Selecione "slack"
4. Cole seu Bot Token do Slack
5. Clique em "Salvar Chave"

**Como obter Bot Token do Slack:**
1. Acesse https://api.slack.com/apps
2. Crie um novo app ou selecione um existente
3. Vá para "OAuth & Permissions"
4. Adicione scopes: `chat:write`, `channels:read`
5. Instale o app no workspace
6. Copie o "Bot User OAuth Token"

## Comandos Avançados

### Especificar Data Exata
```
Marque reunião no dia 25/01/2024 às 10h
```

### Especificar Duração
```
Marque uma reunião de 2 horas amanhã às 14h chamada 'Workshop de Design'
```

### Múltiplos Canais do Slack
```
Avise nos canais #dev e #design que a reunião foi marcada
```
*(Nota: pode precisar de ajustes no MCP do Slack para suportar múltiplos canais)*

## Troubleshooting

### Erro: "Credenciais não configuradas"
- Verifique se você conectou sua conta Google no Painel de Controle
- Verifique se configurou a chave do Slack (se necessário)

### Erro: "Google OAuth não configurado"
- Verifique se `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` estão no arquivo `.env`
- Certifique-se de que o arquivo `.env` está na raiz do projeto

### Erro: "Ferramenta não encontrada"
- Verifique se o nome da ferramenta está correto
- Verifique se o MCP foi registrado no `mcp_hub.py`

### Erro: "Não foi possível conectar ao backend"
- Certifique-se de que o backend está rodando em `http://localhost:8000`
- Verifique se não há firewall bloqueando a conexão

## Dicas

1. **Use linguagem natural**: O sistema entende comandos coloquiais
2. **Seja específico**: Quanto mais detalhes, melhor a execução
3. **Verifique credenciais**: Sempre configure as ferramentas antes de usar
4. **Teste com comandos simples**: Comece com uma ferramenta por vez
5. **Use o Painel de Controle**: Verifique quais ferramentas estão configuradas

