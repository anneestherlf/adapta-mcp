# Arquitetura do Gateway Inteligente

## Visão Geral

O Gateway Inteligente é um sistema que traduz comandos em linguagem natural em ações executadas em múltiplas APIs, com gerenciamento centralizado de segurança e autenticação.

## Componentes Principais

### Passo 0: Painel de Controle
**Arquivo**: `frontend/app.py` (aba "Painel de Controle")

**Responsabilidade**: Configuração inicial de ferramentas e credenciais

**Tipos de Autenticação**:
- **Tipo A (OAuth 2.0)**: Para APIs de usuário (ex: Google Calendar)
  - Usuário autoriza via tela de login
  - Sistema recebe `refresh_token` (chave mestra de longa duração)
  - Armazenado no Cofre associado ao `user_id`
  
- **Tipo B (Chave Estática)**: Para APIs de sistema (ex: Slack)
  - Administrador insere chave de API
  - Armazenada no Cofre como credencial global

### Passo 1: Interface de Apresentação
**Arquivo**: `frontend/app.py`

**Responsabilidade**: Interface web onde usuário digita comandos

**Tecnologia**: Streamlit

**Funcionalidades**:
- Campo de entrada para comandos em linguagem natural
- Exibição de respostas consolidadas
- Navegação entre páginas (Executar, Painel, Status)

### Passo 2: Gateway Unificado
**Arquivo**: `backend/main.py`

**Responsabilidade**: Ponto único de entrada para todas as requisições

**Tecnologia**: FastAPI

**Endpoints**:
- `POST /api/execute`: Recebe comando e executa
- `POST /api/admin/configure-tool`: Configura ferramenta
- `GET /api/admin/tools`: Lista ferramentas configuradas
- `GET /api/auth/google/authorize`: Inicia OAuth Google
- `GET /api/auth/google/callback`: Callback OAuth Google

**Benefícios**:
- Centralização de tráfego
- Facilita segurança e monitoramento
- Ponto único de gerenciamento

### Passo 3: Roteamento Inteligente
**Arquivo**: `backend/router.py`

**Responsabilidade**: Interpreta comandos e gera plano de execução

**Tecnologia**: Google Gemini (LLM)

**Processo**:
1. Recebe prompt do usuário
2. Analisa com LLM
3. Identifica ferramentas necessárias
4. Extrai parâmetros de cada ferramenta
5. Gera `ExecutionPlan` com lista de ações

**Exemplo**:
```
Input: "Marque reunião amanhã 10h e avise no Slack"
Output: {
  "actions": [
    {"tool_name": "google_calendar", "parameters": {...}},
    {"tool_name": "slack", "parameters": {...}}
  ]
}
```

### Passo 4: Hub de MCPs
**Arquivo**: `backend/mcp_hub.py`

**Responsabilidade**: Gerencia e executa ações através dos MCPs

**MCPs Disponíveis**:
- `backend/mcps/google_calendar_mcp.py`: Adaptador para Google Calendar
- `backend/mcps/slack_mcp.py`: Adaptador para Slack

**Características dos MCPs**:
- "Burros" de propósito: não contêm credenciais
- Contêm apenas lógica de uso da API
- Recebem `access_token` do Cofre quando necessário
- Fáceis de adicionar novos (basta criar novo arquivo)

### Passo 5: Cofre de Chaves
**Arquivo**: `backend/vault.py`

**Responsabilidade**: Gerenciamento centralizado e seguro de credenciais

**Funcionalidades**:
- Armazenamento criptografado de credenciais
- Gerenciamento de refresh_tokens (Tipo A)
- Gerenciamento de chaves estáticas (Tipo B)
- Renovação automática de access_tokens
- Separação por usuário (Tipo A) e global (Tipo B)

**Segurança**:
- Criptografia usando Fernet (AES-128)
- Chave de criptografia armazenada separadamente
- Credenciais nunca expostas aos MCPs

**Fluxo Tipo A (Google Calendar)**:
1. MCP solicita access_token para `user_id`
2. Cofre busca refresh_token do usuário
3. Cofre usa refresh_token para obter novo access_token
4. Cofre retorna access_token temporário
5. MCP usa access_token (expira logo depois)

**Fluxo Tipo B (Slack)**:
1. MCP solicita token do Slack
2. Cofre busca chave estática
3. Cofre retorna chave
4. MCP usa chave diretamente

### Passo 6: Consolidação de Respostas
**Arquivo**: `backend/router.py` (método `consolidate_response`)

**Responsabilidade**: Agrega múltiplas respostas em uma única resposta amigável

**Processo**:
1. Recebe resultados de todas as ações executadas
2. Usa LLM para criar resposta consolidada
3. Retorna resposta em linguagem natural

**Exemplo**:
```
Input: [
  {"tool_name": "google_calendar", "status": "success", ...},
  {"tool_name": "slack", "status": "success", ...}
]
Output: "Pronto! Marquei a 'Reunião de Alinhamento' no seu Google Calendar e avisei o canal #projetos no Slack."
```

## Fluxo Completo

```
1. Usuário digita comando na Interface (Passo 1)
   ↓
2. Interface envia para Gateway (Passo 2)
   ↓
3. Gateway chama Router (Passo 3)
   ↓
4. Router usa LLM para gerar ExecutionPlan
   ↓
5. Gateway chama MCPHub (Passo 4) para cada ação
   ↓
6. MCPHub solicita credenciais ao Vault (Passo 5)
   ↓
7. Vault retorna access_token/token
   ↓
8. MCP executa ação na API externa
   ↓
9. MCP retorna resultado
   ↓
10. Gateway consolida respostas (Passo 6)
   ↓
11. Gateway retorna resposta consolidada
   ↓
12. Interface exibe resultado ao usuário
```

## Estrutura de Diretórios

```
mcp2/
├── backend/
│   ├── __init__.py
│   ├── main.py              # Gateway Unificado (Passo 2)
│   ├── router.py            # Roteamento Inteligente (Passo 3, 6)
│   ├── vault.py             # Cofre de Chaves (Passo 5)
│   ├── mcp_hub.py           # Hub de MCPs (Passo 4)
│   ├── utils.py             # Utilitários
│   └── mcps/
│       ├── __init__.py
│       ├── google_calendar_mcp.py
│       └── slack_mcp.py
├── frontend/
│   ├── __init__.py
│   └── app.py               # Interface + Painel (Passo 0, 1)
├── credentials/             # Gerado automaticamente
│   ├── vault.json          # Credenciais criptografadas
│   └── .encryption_key     # Chave de criptografia
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── setup.py
└── .env                     # Variáveis de ambiente (criar manualmente)
```

## Extensibilidade

### Adicionar Nova Ferramenta

1. **Criar MCP** (`backend/mcps/nova_ferramenta_mcp.py`):
```python
class NovaFerramentaMCP:
    async def execute(self, access_token: str, parameters: Dict[str, Any]):
        # Lógica para usar a API
        pass
```

2. **Registrar no Hub** (`backend/mcp_hub.py`):
```python
self.mcps["nova_ferramenta"] = NovaFerramentaMCP()
```

3. **Adicionar ao Router** (`backend/router.py`):
```python
self.available_tools.append({
    "name": "nova_ferramenta",
    "description": "...",
    "parameters": {...}
})
```

4. **Configurar Credenciais**:
   - Via Painel de Controle (Tipo A ou B)
   - Ou diretamente no Vault

## Segurança

- **Criptografia**: Todas as credenciais são criptografadas antes de salvar
- **Separação**: MCPs nunca têm acesso direto a credenciais
- **Tokens Temporários**: Access_tokens expiram rapidamente
- **Refresh Tokens**: Armazenados de forma segura e usados apenas quando necessário
- **Validação**: OAuth 2.0 com state para prevenir CSRF

## Próximos Passos

- [ ] Adicionar mais ferramentas (WhatsApp, Mercado Livre, etc.)
- [ ] Implementar cache de tokens
- [ ] Adicionar logs e monitoramento
- [ ] Implementar rate limiting
- [ ] Adicionar testes automatizados
- [ ] Melhorar tratamento de erros
- [ ] Adicionar suporte a múltiplos idiomas

