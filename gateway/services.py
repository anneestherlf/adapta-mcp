"""
Serviço central do Gateway: roteia comandos do usuário para MCPs (adaptadores)
usando um LLM (quando disponível) ou um roteador rule-based de fallback.

Objetivos principais do módulo:
- Definir wrappers (call_*) para cada MCP
- Oferecer a função `processar_comando_com_llm(prompt)` que retorna um
  dicionário padronizado {status, data/message}

Requisitos de robustez:
- Se a chave do Gemini não estiver presente, usamos um roteador simples
  baseado em regras para permitir testes locais e facilitar o desenvolvimento.
"""

from typing import Any, Callable, Dict
import re
import logging

from gateway.config import settings
from gateway import mcp_registry, credentials

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Import dos MCPs
from mcps.mcp_mercadolivre import search_mercadolivre
from mcps.mcp_figma import get_figma_info


def call_mercadolivre_search(query: str) -> dict:
    """Wrapper para o MCP Mercado Livre.

    Args:
        query: termos de busca (string)

    Returns:
        dict: resposta padronizada do MCP
    """
    logger.info("[Gateway] Roteando para MCP Mercado Livre: %s", query)
    api_key = getattr(settings, "mercadolivre_api_key", None)
    return search_mercadolivre(query=query, api_key=api_key)


def call_figma_info(file_id: str) -> dict:
    """Wrapper para o MCP Figma.

    Args:
        file_id: ID/Key do arquivo Figma
    """
    logger.info("[Gateway] Roteando para MCP Figma: %s", file_id)
    api_key = getattr(settings, "figma_api_key", None)
    return get_figma_info(file_id=file_id, api_key=api_key)


# Ferramentas disponíveis (nome -> função)
tools_disponiveis: Dict[str, Callable[..., Any]] = {
    "call_mercadolivre_search": call_mercadolivre_search,
    "call_figma_info": call_figma_info,
}


def _reload_dynamic_tools():
    """Recarrega MCPs registrados dinamicamente e atualiza tools_disponiveis."""
    dynamic = mcp_registry.load_all_tools(credentials.get_credential)
    # dynamic keys are service names as registered; avoid overwriting core tools
    for k, v in dynamic.items():
        if k in tools_disponiveis:
            # prefix custom tools to avoid collision
            tools_disponiveis[f"custom_{k}"] = v
        else:
            tools_disponiveis[k] = v


# Carrega dinamicamente no startup
_reload_dynamic_tools()


def _simple_router(prompt: str) -> dict:
    """Roteador de fallback: determina a ferramenta a chamar sem LLM.

    Estratégia:
    - Se aparecer 'figma' tenta extrair um file_id (sequência alfanumérica longa)
      e chama `call_figma_info`.
    - Caso contenha 'mercado' ou 'mercado livre' ou 'buscar' -> chama Mercado Livre
      usando o prompt inteiro como query.
    - Caso contrário, tenta chamar Mercado Livre por padrão.
    """
    low = prompt.lower()
    # Figma
    if "figma" in low:
        # 1) tenta extrair file id diretamente (chars alfanum de 8+)
        m = re.search(r"([A-Za-z0-9_-]{8,})", prompt)
        if m:
            file_id = m.group(1)
            return call_figma_info(file_id=file_id)

        # 2) tenta extrair a key de uma URL completa do Figma
        m2 = re.search(r"figma\.com\/file\/([A-Za-z0-9_-]+)", prompt, flags=re.IGNORECASE)
        if m2:
            file_id = m2.group(1)
            return call_figma_info(file_id=file_id)

        # 3) usa um file_id padrão salvo nas credenciais (chave 'default_file_id')
        default_file = credentials.get_credential("figma", "default_file_id")
        if default_file:
            return call_figma_info(file_id=default_file)

        # 4) fallback amigável: informa como o usuário deve fornecer o file_id
        return {
            "status": "info",
            "data": (
                "Não identifiquei um file_id do Figma no seu comando.\n"
                "Por favor forneça o file key (ex: ABcDeF12Gh34) ou a URL completa do arquivo.\n"
                "Alternativamente, registre um file padrão com: /admin/set-credential (service='figma', key='default_file_id', value='<FILE_KEY>')."
            ),
        }

    # Mercado Livre
    if "mercado" in low or "mercado livre" in low or "buscar" in low or "procura" in low:
        return call_mercadolivre_search(query=prompt)

    # Default: tenta Mercado Livre
    return call_mercadolivre_search(query=prompt)


def processar_comando_com_llm(prompt: str) -> dict:
    """Ponto central: recebe um prompt e retorna resposta consolidada.

    Se `settings.gemini_api_key` estiver configurada, tentamos usar o Gemini
    com Function Calling. Caso contrário, usamos o roteador _simple_router.
    """
    logger.info("[Gateway] Recebido novo comando: %s", prompt)

    # Tenta usar Gemini se houver chave
    gemini_key = getattr(settings, "gemini_api_key", None)
    if not gemini_key:
        logger.info("[Gateway] Gemini não configurado: usando roteador de fallback.")
        try:
            result = _simple_router(prompt)
            return {"status": "success" if result.get("status") == "success" else result.get("status", "info"), "data": result.get("data") if result.get("status")=="success" else result.get("message")}
        except Exception as e:
            logger.exception("Erro no roteador fallback")
            return {"status": "error", "message": str(e)}

    # Se chegamos aqui, há uma chave Gemini: tentamos integrar com google.generativeai
    try:
        import google.generativeai as genai

        genai.configure(api_key=gemini_key)

        # Declarações de função para o modelo (o SDK gera a partir da função)
        tool_defs = [
            genai.Tool(
                function_declarations=[genai.FunctionDeclaration.from_function(func) for func in tools_disponiveis.values()]
            )
        ]

        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest", tools=tool_defs)
        chat = model.start_chat()

        # Envia prompt
        response = chat.send_message(prompt)

        # Tenta extrair function_calls de forma defensiva
        function_calls = []
        try:
            function_calls = response.candidates[0].content.parts[0].function_calls
        except Exception:
            function_calls = []

        if not function_calls:
            logger.info("[Gateway] LLM não pediu function_call — retornando texto simples.")
            return {"status": "info", "data": getattr(response, "text", str(response))}

        call = function_calls[0]
        tool_name = call.name
        tool_args = {k: v for k, v in call.args.items()}

        if tool_name not in tools_disponiveis:
            return {"status": "error", "message": f"Ferramenta '{tool_name}' desconhecida pelo Gateway."}

        logger.info("[Gateway] LLM solicitou: %s com %s", tool_name, tool_args)
        func = tools_disponiveis[tool_name]
        resultado_mcp = func(**tool_args)

        # Envia o resultado do MCP de volta ao LLM para gerar resposta em linguagem natural
        followup = chat.send_message(genai.Part(function_response=genai.FunctionResponse(name=tool_name, response=resultado_mcp)))

        return {"status": "success", "data": getattr(followup, "text", str(followup))}

    except Exception as e:
        logger.exception("Erro ao usar Gemini; retornando erro.")
        return {"status": "error", "message": str(e)}
