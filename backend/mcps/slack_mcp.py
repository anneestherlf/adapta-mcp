"""
MCP para Slack
Adaptador que sabe como enviar mensagens no Slack
"""
from typing import Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackMCP:
    """
    Adaptador para Slack API
    Não contém credenciais - recebe token do Cofre
    """
    
    def __init__(self):
        pass
    
    async def execute(
        self,
        access_token: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Envia mensagem no Slack
        
        Args:
            access_token: Bot token do Slack (obtido do Cofre)
            parameters: {
                "channel": str (ex: "#projetos" ou "C1234567890"),
                "message": str
            }
        """
        try:
            client = WebClient(token=access_token)
            
            channel = parameters.get('channel', '#general')
            message = parameters.get('message', '')
            
            # Se o canal começa com #, converter para ID
            if channel.startswith('#'):
                channel_name = channel[1:]
                # Tentar encontrar o canal pelo nome
                try:
                    channels = client.conversations_list()
                    channel_id = None
                    for ch in channels['channels']:
                        if ch['name'] == channel_name:
                            channel_id = ch['id']
                            break
                    
                    if not channel_id:
                        # Tentar usar o nome diretamente (pode funcionar em alguns casos)
                        channel_id = channel
                except:
                    channel_id = channel
            else:
                channel_id = channel
            
            # Enviar mensagem
            response = client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            
            return {
                "ts": response['ts'],
                "channel": response['channel'],
                "message": {
                    "text": response['message']['text']
                }
            }
        
        except SlackApiError as e:
            raise Exception(f"Erro ao enviar mensagem no Slack: {e.response['error']}")
        except Exception as e:
            raise Exception(f"Erro ao enviar mensagem no Slack: {str(e)}")

