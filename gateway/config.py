from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str
    mercadolivre_api_key: str
    figma_api_key: str

# Instância única que será importada por outros módulos
settings = Settings()