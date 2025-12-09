"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_env: str = "local"
    app_debug: bool = True

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    database_url: str

    # Neo4j
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str

    # Google AI
    google_api_key: str
    gemini_model: str = "gemini-2.5-flash-preview-05-20"
    embedding_model: str = "text-embedding-004"

    # CLIP (optional)
    huggingface_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
