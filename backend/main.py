"""
Gateway Unificado - Backend principal
Passo 2: O "Porteiro" - ponto único de entrada para todas as requisições
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import uvicorn

# Carregar variáveis de ambiente
load_dotenv()

from backend.router import Router
from backend.vault import Vault
from backend.mcp_hub import MCPHub

app = FastAPI(title="Gateway Inteligente", version="1.0.0")

# CORS para permitir comunicação com frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
router = Router()
vault = Vault()
mcp_hub = MCPHub(vault)


class UserRequest(BaseModel):
    """Modelo para requisição do usuário"""
    prompt: str
    user_id: Optional[str] = "default_user"


class ToolConfig(BaseModel):
    """Modelo para configuração de ferramenta"""
    tool_name: str
    tool_type: str  # "user_oauth" ou "system_static"
    credentials: Dict[str, Any]


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Gateway Inteligente - Adapta MCP",
        "status": "operational",
        "version": "1.0.0"
    }


@app.post("/api/execute")
async def execute_command(request: UserRequest):
    """
    Endpoint principal: recebe comando em linguagem natural e executa
    Passo 2: Gateway Unificado
    """
    try:
        # Passo 3: Roteamento Inteligente
        plan = await router.plan_execution(request.prompt, request.user_id)
        
        # Passo 4: Executar ações via Hub de MCPs
        results = []
        for action in plan.actions:
            result = await mcp_hub.execute_action(
                action.tool_name,
                action.parameters,
                request.user_id
            )
            results.append(result)
        
        # Passo 6: Consolidação de Respostas
        consolidated_response = await router.consolidate_response(
            request.prompt,
            results
        )
        
        return {
            "success": True,
            "response": consolidated_response,
            "details": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/configure-tool")
async def configure_tool(config: ToolConfig):
    """
    Passo 0: Painel de Controle - Configurar ferramenta
    """
    try:
        vault.store_credentials(
            tool_name=config.tool_name,
            tool_type=config.tool_type,
            credentials=config.credentials
        )
        return {"success": True, "message": f"Ferramenta {config.tool_name} configurada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/tools")
async def list_tools():
    """Lista todas as ferramentas configuradas"""
    return vault.list_tools()


@app.get("/api/auth/google/authorize")
async def google_authorize(user_id: str = "default_user"):
    """
    Passo 0: Iniciar fluxo OAuth do Google
    """
    try:
        auth_url, state = vault.get_google_oauth_url(state=user_id)
        return {"auth_url": auth_url, "state": state}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/auth/google/callback")
@app.get("/auth/google/callback")  # Rota alternativa sem /api
async def google_callback(code: str, state: Optional[str] = None):
    """
    Passo 0: Callback OAuth do Google
    Suporta ambas as rotas: /api/auth/google/callback e /auth/google/callback
    """
    try:
        # Usar state como user_id se fornecido, senão usar default
        user_id = state if state else "default_user"
        credentials = await vault.handle_google_oauth_callback(code, user_id, state)
        
        # Retornar página HTML amigável
        from fastapi.responses import HTMLResponse
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Autorização Concluída</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                }}
                h1 {{
                    color: #667eea;
                }}
                .success {{
                    color: #28a745;
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✅</div>
                <h1>Conta Google Conectada!</h1>
                <p>Sua conta Google foi conectada com sucesso.</p>
                <p>Você pode fechar esta janela e voltar ao Gateway Inteligente.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        # Retornar página de erro amigável também
        from fastapi.responses import HTMLResponse
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro na Autorização</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                }}
                h1 {{
                    color: #ff6b6b;
                }}
                .error {{
                    color: #ff6b6b;
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">❌</div>
                <h1>Erro na Autorização</h1>
                <p>Ocorreu um erro ao conectar sua conta Google.</p>
                <p><strong>Erro:</strong> {str(e)}</p>
                <p>Tente novamente ou verifique as configurações.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

