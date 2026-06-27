from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    ai_provider: str = "openrouter"
    database_url: str

    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "deepseek/deepseek-chat:free"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")
    postgres_user: str
    postgres_password: str
    postgres_db: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"


settings = Settings()
