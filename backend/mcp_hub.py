"""
Hub de MCPs - Sala de Máquinas
Passo 4: Adaptadores para cada ferramenta/API
"""
from typing import Dict, Any, Optional
from backend.vault import Vault

# Importar MCPs
from backend.mcps.google_calendar_mcp import GoogleCalendarMCP
from backend.mcps.slack_mcp import SlackMCP

class MCPHub:
    """
    Gerencia e executa ações através dos MCPs (Model Context Protocols)
    Cada MCP é um adaptador "burro" que sabe como usar uma API específica
    """
    
    def __init__(self, vault: Vault):
        self.vault = vault
        self.mcps = {
            "google_calendar": GoogleCalendarMCP(),
            "slack": SlackMCP()
        }
    
    async def execute_action(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Executa uma ação através do MCP apropriado
        
        Args:
            tool_name: Nome da ferramenta (ex: "google_calendar")
            parameters: Parâmetros da ação
            user_id: ID do usuário
            
        Returns:
            Resultado da execução
        """
        if tool_name not in self.mcps:
            return {
                "status": "error",
                "tool_name": tool_name,
                "error": f"Ferramenta {tool_name} não encontrada"
            }
        
        # Obter credenciais do cofre
        access_token = self.vault.get_access_token(tool_name, user_id)
        if not access_token:
            return {
                "status": "error",
                "tool_name": tool_name,
                "error": f"Credenciais não configuradas para {tool_name}"
            }
        
        # Executar ação via MCP
        mcp = self.mcps[tool_name]
        try:
            result = await mcp.execute(access_token, parameters)
            return {
                "status": "success",
                "tool_name": tool_name,
                "details": result
            }
        except Exception as e:
            return {
                "status": "error",
                "tool_name": tool_name,
                "error": str(e)
            }

