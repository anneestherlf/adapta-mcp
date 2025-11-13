import requests

# Constante para a URL base da API do Figma
FIGMA_API_BASE_URL = "https://api.figma.com/v1"

def get_figma_info(file_id: str, api_key: str) -> dict:
    """
    Busca informações de um arquivo no Figma usando a API.
    
    Args:
        file_id (str): O ID (ou 'key') do arquivo no Figma.
        api_key (str): O Personal Access Token para autenticação.
        
    Returns:
        dict: Um dicionário padronizado com o status e os dados.
    """
    print(f"[MCP-Figma] Buscando informações do arquivo: {file_id}")
    
    # A API do Figma espera a chave no header 'X-Figma-Token'
    # Esta é a principal diferença de autenticação em relação ao Mercado Livre
    headers = {
        "X-Figma-Token": api_key
    }
    
    # Endpoint para buscar informações do arquivo
    endpoint_url = f"{FIGMA_API_BASE_URL}/files/{file_id}"
    
    try:
        response = requests.get(endpoint_url, headers=headers)
        
        # Lança uma exceção para erros HTTP (como 403, 404, 500)
        response.raise_for_status() 
        
        data = response.json()
        
        # O JSON completo do Figma é enorme.
        # Vamos selecionar apenas os dados principais para a PoC.
        simplified_data = {
            "name": data.get("name"),
            "lastModified": data.get("lastModified"),
            "thumbnailUrl": data.get("thumbnailUrl"),
            "file_key": file_id
        }
        
        return {"status": "success", "data": simplified_data}
        
    except requests.exceptions.HTTPError as http_err:
        # Erros comuns de API
        if http_err.response.status_code == 404:
            return {"status": "error", "message": f"Arquivo do Figma não encontrado (ID: {file_id})."}
        if http_err.response.status_code == 403:
            return {"status": "error", "message": "Acesso negado. Verifique sua chave de API do Figma e as permissões do arquivo."}
        
        return {"status": "error", "message": f"Erro HTTP ao acessar o Figma: {http_err}"}
    except Exception as e:
        # Captura genérica para outros erros (ex: falha de conexão)
        return {"status": "error", "message": str(e)}