"""
MCP para Google Calendar
Adaptador que sabe como criar eventos no Google Calendar
"""
from typing import Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os

class GoogleCalendarMCP:
    """
    Adaptador para Google Calendar API
    Não contém credenciais - recebe access_token do Cofre
    """
    
    def __init__(self):
        self.service = None
    
    async def execute(
        self,
        access_token: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria um evento no Google Calendar
        
        Args:
            access_token: Token de acesso (obtido do Cofre)
            parameters: {
                "title": str,
                "start_time": str (ISO 8601),
                "end_time": str (ISO 8601),
                "description": str (opcional)
            }
        """
        try:
            # Criar credenciais a partir do token
            creds = Credentials(token=access_token)
            
            # Construir serviço
            service = build('calendar', 'v3', credentials=creds)
            
            # Preparar evento
            event = {
                'summary': parameters.get('title', 'Novo Evento'),
                'description': parameters.get('description', ''),
                'start': {
                    'dateTime': parameters.get('start_time'),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': parameters.get('end_time'),
                    'timeZone': 'America/Sao_Paulo',
                },
            }
            
            # Criar evento
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                "event_id": created_event.get('id'),
                "html_link": created_event.get('htmlLink'),
                "summary": created_event.get('summary'),
                "start": created_event.get('start'),
                "end": created_event.get('end')
            }
        
        except Exception as e:
            raise Exception(f"Erro ao criar evento no Google Calendar: {str(e)}")

