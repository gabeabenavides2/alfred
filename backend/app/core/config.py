from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str

    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")
    postgres_user: str
    postgres_password: str
    postgres_db: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    alfred_system_prompt: str = "You are Alfred, a helpful personal AI assistant."
    openrouter_site_url: str = "http://localhost:3000"
    openrouter_app_name: str = "Alfred"
    llm_provider: str = "openrouter"


settings = Settings()
