from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Database
    database_url: str

    # OpenRouter connection
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_site_url: str = "http://localhost:3000"
    openrouter_app_name: str = "Alfred"

    # Authentication
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    # Alfred
    alfred_system_prompt: str = (
        "You are Alfred, a helpful personal AI assistant."
    )

    # Orchestrator
    orchestrator_provider: str
    orchestrator_model: str

    # Chat
    chat_provider: str
    chat_model: str

    # Reasoning
    reasoning_provider: str
    reasoning_model: str

    # Embeddings
    embedding_provider: str
    embedding_model: str
    embedding_dimensions: int

    # Vision
    vision_provider: str
    vision_model: str | None = None

    # Web
    web_provider: str
    web_model: str | None = None

    # Video
    video_provider: str
    video_model: str | None = None

    # Speech-to-text
    stt_provider: str
    stt_model: str | None = None

    # Text-to-speech
    tts_provider: str
    tts_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = Settings()