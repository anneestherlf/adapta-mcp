# adapta-mcp

# Gateway Central Inteligente (Trilha 2 - Inteli Academy)

Este repositório demonstra uma arquitetura simples onde um Gateway
recebe comandos em linguagem natural do frontend, usa um LLM (opcional)
para decidir quais adaptadores (MCPs) acionar e consolida respostas de
várias APIs externas (ex.: Mercado Livre, Figma).

Estrutura principal

/adapta-mcp
|
|-- 📂 gateway/
|   |-- __init__.py
|   |-- main.py         (Backend FastAPI — pontos de entrada e métricas)
|   |-- services.py     (Roteador/integração com LLM e MCPs)
|   |-- config.py       (Gerenciamento de chaves via .env)
|   |-- observability.py (Logging e métricas simples)
|
|-- 📂 mcps/
|   |-- __init__.py
|   |-- mcp_mercadolivre.py (Adaptador Mercado Livre — busca pública)
|   |-- mcp_figma.py        (Adaptador Figma)
|
|-- 📂 frontend/
|   |-- app.py          (App Streamlit — UI mínima)
|
|-- .env                (Onde as chaves de API secretas ficarão)
|-- .env.example        (Exemplo de variáveis de ambiente)
|-- .gitignore
|-- requirements.txt

Objetivo desta atualização

- Tornar o projeto executável localmente sem dependência imediata do LLM,
	oferecendo um roteador de fallback que usa MCPs implementados (ex.:
	`mcps/mcp_mercadolivre.py`) para testes.
- Adicionar logging e métricas simples(in memory) expostas em `/metrics`.

Como rodar (Windows / PowerShell)

1) Crie um virtualenv e ative:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2) Instale dependências:

```powershell
pip install -r requirements.txt
```

3) Configure variáveis de ambiente:

- Copie `.env.example` para `.env` e preencha as chaves se desejar usar o
	Gemini ou Figma. Para desenvolvimento local, deixar `GEMINI_API_KEY` vazio
	faz com que o Gateway use o roteador de fallback.

4) Rodar o Gateway (FastAPI):

```powershell
uvicorn gateway.main:app --reload --host 127.0.0.1 --port 8000
```

Endpoints úteis

- POST /process-command  — recebe JSON {"prompt": "<seu comando>"}
	- Ex.: {"prompt":"Buscar iPhone 15 no Mercado Livre"}
- GET /         — health-check
- GET /metrics  — retorna métricas simples em JSON (requests_total,
	requests_success, requests_error, last_request_latency_ms)

5) Rodar o frontend Streamlit (em outra janela/terminal):

```powershell
streamlit run frontend/app.py
```

Exemplos de prompts para testar

- "Buscar iPhone 15 no Mercado Livre"
- "Procure por monitor 27 polegadas no Mercado Livre"
- "Mostre informações do arquivo Figma ABCDEFGH" (precisa de file id e API Key)

Próximos passos recomendados

- Implementar `mcps/mcp_mercadolivre.py` com mais campos e paginação (já
	existe uma implementação PoC que busca 5 resultados públicos).
- Tornar endpoints assíncronos para escalabilidade (usar httpx async e
	`async def` no FastAPI).
- Subir métricas para Prometheus ou usar `prometheus_client` para integração
	com observabilidade padrão.
- Adicionar validação Pydantic para o schema de respostas do MCP e testes.

Se quiser, eu posso:
- Transformar o Gateway para async agora (maior mudança).
- Adicionar testes unitários para os MCPs.
- Integrar `prometheus_client` para métricas compatíveis com Prometheus.

Obrigado — diga qual próxima melhoria prefere que eu implemente.