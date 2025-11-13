from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from gateway.services import processar_comando_com_llm
import uvicorn
from gateway import observability
import logging
from gateway import mcp_registry, credentials
from typing import Optional
from pathlib import Path
from gateway import services as gateway_services
from fastapi import Body

app = FastAPI(title="Gateway Central Inteligente")
observability.configure_logging()
logger = logging.getLogger(__name__)

class CommandRequest(BaseModel):
    prompt: str

@app.post("/process-command")
def process_command(request: CommandRequest):
    """
    Endpoint único que recebe o comando do usuário,
    processa com o LLM e retorna a resposta consolidada.
    """
    # A mágica acontece aqui
    observability.incr("requests_total", 1)
    with observability.time_block("last_request_latency_ms"):
        try:
            response = processar_comando_com_llm(request.prompt)
        except Exception as e:
            observability.incr("requests_error", 1)
            logger.exception("Erro ao processar comando")
            return {"status": "error", "message": str(e)}

    # Atualiza métricas de sucesso/erro com base no status retornado
    status = response.get("status")
    if status == "success":
        observability.incr("requests_success", 1)
    else:
        observability.incr("requests_error", 1)

    return response


@app.post("/admin/register-mcp")
def admin_register_mcp(name: str = Form(...), description: str = Form(""), entrypoint: str = Form("run"), file: UploadFile = File(...)):
    """Endpoint admin para registrar um MCP:
    - name: nome único do MCP
    - description: descrição semântica
    - entrypoint: nome da função dentro do arquivo (default 'run')
    - file: arquivo Python a ser salvo em mcps/custom/<name>.py
    """
    # validação simples do nome
    if not name.isidentifier():
        return {"status": "error", "message": "Nome inválido. Use um identificador Python válido."}

    dest = Path("mcps/custom") / f"{name}.py"
    try:
        content = file.file.read()
        dest.write_bytes(content)
    except Exception as e:
        return {"status": "error", "message": f"Falha ao salvar arquivo: {e}"}

    # registra no registry
    mcp_registry.register_mcp(name=name, filename=f"{name}.py", description=description, entrypoint=entrypoint)

    # reload dynamic tools
    try:
        from gateway.services import _reload_dynamic_tools

        _reload_dynamic_tools()
    except Exception:
        pass

    return {"status": "success", "message": f"MCP '{name}' registrado."}


@app.post("/admin/set-credential")
def admin_set_credential(service: str, key: str, value: str):
    """Define uma credencial para um serviço (armazenamento centralizado PoC)."""
    credentials.set_credential(service, key, value)
    return {"status": "success", "message": "Credencial salva."}


@app.get("/admin/list-mcps")
def admin_list_mcps():
    return {"status": "success", "data": mcp_registry.list_mcp()}


@app.get("/admin/list-credentials")
def admin_list_credentials():
    # WARNING: This endpoint discloses stored credentials; in production restrict access
    return {"status": "success", "data": credentials.list_credentials()}


@app.post("/admin/call-mcp")
def admin_call_mcp(name: str = Form(...), args: dict = Body(default={})):
    """Chama diretamente um MCP registrado (útil para testes sem LLM).

    - name: nome do MCP registrado
    - args: dict dos argumentos a passar para a função
    """
    tools = getattr(gateway_services, 'tools_disponiveis', {})
    func = tools.get(name) or tools.get(f"custom_{name}")
    if not func:
        return {"status": "error", "message": f"MCP '{name}' não encontrado."}
    try:
        result = func(**args)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def health_check():
    return {"status": "Gateway online"}


@app.get("/metrics")
def metrics():
    """Retorna métricas simples em JSON (para PoC / debug)."""
    return observability.get_metrics()

# Permite executar este arquivo diretamente para testes
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)