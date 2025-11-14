"""
Roteamento Inteligente com LLM
Passo 3: O "Cérebro" - interpreta comandos e decide ações
"""
import os
import google.generativeai as genai
from typing import List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from backend.utils import parse_relative_date

class Action(BaseModel):
    """Representa uma ação a ser executada"""
    tool_name: str
    parameters: Dict[str, Any]

class ExecutionPlan(BaseModel):
    """Plano de execução gerado pelo LLM"""
    actions: List[Action]
    reasoning: str

class Router:
    """
    Usa LLM (Gemini) para interpretar comandos em linguagem natural
    e gerar plano de execução com ferramentas e parâmetros
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Lista de ferramentas disponíveis
        self.available_tools = [
            {
                "name": "google_calendar",
                "description": "Criar eventos no Google Calendar",
                "parameters": {
                    "title": "string - Título do evento",
                    "start_time": "string - Data/hora de início (ISO 8601)",
                    "end_time": "string - Data/hora de fim (ISO 8601)",
                    "description": "string (opcional) - Descrição do evento"
                }
            },
            {
                "name": "slack",
                "description": "Enviar mensagens no Slack",
                "parameters": {
                    "channel": "string - Canal ou ID do canal (ex: #projetos)",
                    "message": "string - Mensagem a ser enviada"
                }
            }
        ]
    
    async def plan_execution(
        self,
        prompt: str,
        user_id: str
    ) -> ExecutionPlan:
        """
        Analisa o prompt do usuário e gera plano de execução
        
        Args:
            prompt: Comando em linguagem natural
            user_id: ID do usuário
            
        Returns:
            ExecutionPlan com lista de ações
        """
        tools_description = self._format_tools_description()
        
        system_prompt = f"""Você é um assistente que interpreta comandos em linguagem natural e os converte em ações executáveis.

FERRAMENTAS DISPONÍVEIS:
{tools_description}

INSTRUÇÕES:
1. Analise o comando do usuário
2. Identifique quais ferramentas são necessárias
3. Extraia os parâmetros necessários para cada ferramenta
4. Retorne um JSON com a seguinte estrutura:
{{
    "actions": [
        {{
            "tool_name": "nome_da_ferramenta",
            "parameters": {{"param1": "valor1", "param2": "valor2"}}
        }}
    ],
    "reasoning": "Explicação breve do que será feito"
}}

IMPORTANTE:
- Para datas relativas como "amanhã", "hoje", calcule a data real no formato ISO 8601
- Para horários, use formato ISO 8601 completo (ex: "2024-01-15T10:00:00")
- Se o usuário mencionar "canal #nome", use "#nome" como channel
- Seja preciso na extração de parâmetros
- Se não houver horário de fim especificado, use 1 hora após o início

COMANDO DO USUÁRIO:
{prompt}

RESPOSTA (apenas JSON, sem markdown):"""

        try:
            response = self.model.generate_content(system_prompt)
            response_text = response.text.strip()
            
            # Remover markdown code blocks se houver
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            # Parse JSON
            import json
            plan_data = json.loads(response_text)
            
            # Criar ExecutionPlan
            actions = [
                Action(**action_data)
                for action_data in plan_data.get("actions", [])
            ]
            
            return ExecutionPlan(
                actions=actions,
                reasoning=plan_data.get("reasoning", "")
            )
        
        except Exception as e:
            # Fallback: tentar extrair informações básicas
            return self._fallback_plan(prompt)
    
    def _format_tools_description(self) -> str:
        """Formata descrição das ferramentas para o prompt"""
        desc = []
        for tool in self.available_tools:
            desc.append(f"- {tool['name']}: {tool['description']}")
            desc.append("  Parâmetros:")
            for param, param_desc in tool['parameters'].items():
                desc.append(f"    - {param}: {param_desc}")
        return "\n".join(desc)
    
    def _fallback_plan(self, prompt: str) -> ExecutionPlan:
        """Plano de fallback caso o LLM falhe"""
        # Análise básica de palavras-chave
        actions = []
        prompt_lower = prompt.lower()
        
        if "calendar" in prompt_lower or "evento" in prompt_lower or "reunião" in prompt_lower:
            actions.append(Action(
                tool_name="google_calendar",
                parameters={"title": "Evento", "start_time": "", "end_time": ""}
            ))
        
        if "slack" in prompt_lower or "canal" in prompt_lower:
            actions.append(Action(
                tool_name="slack",
                parameters={"channel": "#general", "message": ""}
            ))
        
        return ExecutionPlan(
            actions=actions,
            reasoning="Plano gerado via fallback (análise de palavras-chave)"
        )
    
    async def consolidate_response(
        self,
        original_prompt: str,
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Consolida múltiplas respostas em uma resposta única e amigável
        Passo 6: O "Porta-Voz"
        """
        consolidation_prompt = f"""Você recebeu um comando do usuário e várias respostas de execução.

COMANDO ORIGINAL:
{original_prompt}

RESULTADOS DA EXECUÇÃO:
{self._format_results(results)}

Crie uma resposta consolidada, amigável e em linguagem natural que:
1. Confirme o que foi feito
2. Seja clara e concisa
3. Use linguagem natural (português brasileiro)
4. Não seja técnica demais

RESPOSTA (apenas texto, sem formatação):"""

        try:
            response = self.model.generate_content(consolidation_prompt)
            return response.text.strip()
        except:
            # Fallback: resposta simples
            return self._simple_consolidation(results)
    
    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """Formata resultados para o prompt de consolidação"""
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"Ação {i}:")
            formatted.append(f"  Ferramenta: {result.get('tool_name', 'desconhecida')}")
            formatted.append(f"  Status: {result.get('status', 'desconhecido')}")
            formatted.append(f"  Detalhes: {result.get('details', {})}")
        return "\n".join(formatted)
    
    def _simple_consolidation(self, results: List[Dict[str, Any]]) -> str:
        """Consolidação simples sem LLM"""
        success_count = sum(1 for r in results if r.get("status") == "success")
        total = len(results)
        
        if success_count == total:
            return f"Pronto! Executei {total} ação(ões) com sucesso."
        else:
            return f"Executei {success_count} de {total} ação(ões) com sucesso. Algumas ações podem ter falhado."

