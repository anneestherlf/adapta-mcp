"""
Cofre de Chaves - Gerenciamento Centralizado de Credenciais
Passo 5: O "Cofre" - segurança e autenticação centralizada
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Vault:
    """
    Gerencia credenciais de forma centralizada e segura.
    Suporta dois tipos:
    - Tipo A: OAuth 2.0 (refresh_token para APIs de usuário)
    - Tipo B: Chaves estáticas (tokens para APIs de sistema)
    """
    
    def __init__(self):
        self.storage_path = "credentials/vault.json"
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Carregar dados existentes
        self.data = self._load_data()
        
        # Configurações OAuth Google
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        
        # Scopes do Google Calendar
        self.google_scopes = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ]
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Gera ou recupera chave de criptografia"""
        key_file = "credentials/.encryption_key"
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def _load_data(self) -> Dict[str, Any]:
        """Carrega dados do cofre"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "rb") as f:
                    encrypted_data = f.read()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode())
            except:
                return {"tools": {}, "users": {}}
        return {"tools": {}, "users": {}}
    
    def _save_data(self):
        """Salva dados no cofre (criptografado)"""
        json_data = json.dumps(self.data)
        encrypted_data = self.cipher.encrypt(json_data.encode())
        with open(self.storage_path, "wb") as f:
            f.write(encrypted_data)
    
    def store_credentials(
        self,
        tool_name: str,
        tool_type: str,
        credentials: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """
        Armazena credenciais no cofre
        
        Args:
            tool_name: Nome da ferramenta (ex: "slack", "google_calendar")
            tool_type: "user_oauth" ou "system_static"
            credentials: Dicionário com credenciais
            user_id: ID do usuário (obrigatório para user_oauth)
        """
        if tool_type == "user_oauth" and not user_id:
            raise ValueError("user_id é obrigatório para ferramentas user_oauth")
        
        if tool_type == "user_oauth":
            if "users" not in self.data:
                self.data["users"] = {}
            if user_id not in self.data["users"]:
                self.data["users"][user_id] = {}
            self.data["users"][user_id][tool_name] = {
                "type": tool_type,
                "credentials": credentials,
                "created_at": datetime.now().isoformat()
            }
        else:  # system_static
            if "tools" not in self.data:
                self.data["tools"] = {}
            self.data["tools"][tool_name] = {
                "type": tool_type,
                "credentials": credentials,
                "created_at": datetime.now().isoformat()
            }
        
        self._save_data()
    
    def get_credentials(
        self,
        tool_name: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Recupera credenciais do cofre
        
        Para user_oauth: busca refresh_token do usuário
        Para system_static: busca chave estática
        """
        # Tentar buscar credenciais de usuário primeiro
        if user_id and "users" in self.data:
            if user_id in self.data["users"]:
                if tool_name in self.data["users"][user_id]:
                    return self.data["users"][user_id][tool_name]["credentials"]
        
        # Buscar credenciais de sistema
        if "tools" in self.data:
            if tool_name in self.data["tools"]:
                return self.data["tools"][tool_name]["credentials"]
        
        return None
    
    def get_access_token(
        self,
        tool_name: str,
        user_id: str
    ) -> Optional[str]:
        """
        Obtém access_token válido para uma ferramenta
        
        Para Google Calendar:
        - Busca refresh_token do usuário
        - Usa refresh_token para obter novo access_token
        - Retorna access_token temporário
        """
        if tool_name == "google_calendar":
            creds_data = self.get_credentials(tool_name, user_id)
            if not creds_data:
                return None
            
            # Criar objeto Credentials do Google
            creds = Credentials(
                token=creds_data.get("token"),
                refresh_token=creds_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.google_client_id,
                client_secret=self.google_client_secret,
                scopes=self.google_scopes
            )
            
            # Atualizar token se necessário
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    # Salvar token atualizado
                    self.store_credentials(
                        tool_name="google_calendar",
                        tool_type="user_oauth",
                        credentials={
                            "token": creds.token,
                            "refresh_token": creds.refresh_token,
                            "expiry": creds.expiry.isoformat() if creds.expiry else None
                        },
                        user_id=user_id
                    )
            
            return creds.token
        
        elif tool_name == "slack":
            # Para Slack, retorna o token estático diretamente
            creds_data = self.get_credentials(tool_name)
            if creds_data:
                return creds_data.get("token")
            return None
        
        return None
    
    def get_google_oauth_url(self, state: Optional[str] = None) -> tuple:
        """
        Gera URL de autorização OAuth do Google
        
        Returns:
            Tupla (authorization_url, state)
        """
        if not self.google_client_id or not self.google_client_secret:
            raise ValueError("Google OAuth não configurado. Configure GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no .env")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.google_client_id,
                    "client_secret": self.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.google_redirect_uri]
                }
            },
            scopes=self.google_scopes,
            redirect_uri=self.google_redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=state
        )
        return authorization_url, state
    
    async def handle_google_oauth_callback(
        self,
        code: str,
        user_id: str,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa callback OAuth do Google e salva refresh_token
        
        Args:
            code: Código de autorização retornado pelo Google
            user_id: ID do usuário (pode vir do state)
            state: State retornado pelo Google (pode conter user_id)
        """
        # Se state foi fornecido e user_id não, usar state como user_id
        if state and not user_id:
            user_id = state
        
        if not self.google_client_id or not self.google_client_secret:
            raise ValueError("Google OAuth não configurado")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.google_client_id,
                    "client_secret": self.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.google_redirect_uri]
                }
            },
            scopes=self.google_scopes,
            redirect_uri=self.google_redirect_uri
        )
        
        # Trocar código por tokens
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Salvar refresh_token no cofre
        self.store_credentials(
            tool_name="google_calendar",
            tool_type="user_oauth",
            credentials={
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "expiry": creds.expiry.isoformat() if creds.expiry else None
            },
            user_id=user_id
        )
        
        return {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "expiry": creds.expiry.isoformat() if creds.expiry else None
        }
    
    def list_tools(self) -> Dict[str, Any]:
        """Lista todas as ferramentas configuradas"""
        return {
            "system_tools": list(self.data.get("tools", {}).keys()),
            "user_tools": {
                user_id: list(tools.keys())
                for user_id, tools in self.data.get("users", {}).items()
            }
        }

