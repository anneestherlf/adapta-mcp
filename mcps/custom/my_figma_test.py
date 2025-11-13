"""Exemplo de MCP para Figma pronto para upload no Gateway.

Instruções rápidas:
- Registre este arquivo via endpoint /admin/register-mcp com name='my_figma_test' e entrypoint='run'.
- Salve a credencial do Figma com /admin/set-credential service='figma' key='api_key' value='<SEU_TOKEN>'.
- Opcional: defina default_file_id com key='default_file_id' para testes sem informar file_id.

Assinatura esperada: run(file_id: str, api_key: str | None = None) -> dict
Retorna um dict serializável com {'status': 'success', 'data': {...}} ou {'status':'error','message':...}
"""
from typing import Optional
import requests


def run(file_id: str, api_key: Optional[str] = None) -> dict:
    """Busca informações simplificadas de um arquivo no Figma.

    Params:
        file_id: key do arquivo Figma (ex: ABcDeF12Gh34)
        api_key: Personal Access Token do Figma (se None, o Gateway pode injetar a credencial)

    Returns:
        dict com chaves 'status' e 'data' ou 'message'
    """
    if not file_id:
        return {"status": "error", "message": "file_id é obrigatório."}

    if not api_key:
        # Sem api_key não conseguimos acessar arquivos privados; devolvemos instrução
        return {"status": "error", "message": "Nenhuma api_key fornecida. Defina uma credencial para 'figma' no Gateway."}

    endpoint = f"https://api.figma.com/v1/files/{file_id}"
    headers = {"X-Figma-Token": api_key}

    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        simplified = {
            "name": data.get("name"),
            "lastModified": data.get("lastModified"),
            "thumbnailUrl": data.get("thumbnailUrl"),
            "file_key": file_id,
        }

        return {"status": "success", "data": simplified}

    except requests.exceptions.HTTPError as he:
        code = getattr(he.response, "status_code", None)
        if code == 403:
            return {"status": "error", "message": "Acesso negado (403). Verifique o token e permissões do arquivo."}
        if code == 404:
            return {"status": "error", "message": "Arquivo não encontrado (404). Verifique o file_id."}
        return {"status": "error", "message": f"HTTP error: {he}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # Pequeno teste local: substitua pelos seus valores
    import os

    file_key = os.environ.get("FIGMA_TEST_FILE")
    token = os.environ.get("FIGMA_TEST_TOKEN")
    print(run(file_key, api_key=token))
