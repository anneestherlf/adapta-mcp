"""
Script de setup inicial
"""
import os
import secrets

def generate_secret_key():
    """Gera uma chave secreta para criptografia"""
    return secrets.token_urlsafe(32)

def setup_env():
    """Cria arquivo .env se não existir"""
    if os.path.exists(".env"):
        print("OK: Arquivo .env ja existe")
        return
    
    print("Criando arquivo .env...")
    
    env_content = f"""# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Slack (opcional - pode ser configurado via painel)
SLACK_BOT_TOKEN=your_slack_bot_token

# Segurança
SECRET_KEY={generate_secret_key()}
ENCRYPTION_KEY={generate_secret_key()[:32]}
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("OK: Arquivo .env criado!")
    print("IMPORTANTE: Configure as variaveis no arquivo .env antes de executar o sistema")

if __name__ == "__main__":
    setup_env()

