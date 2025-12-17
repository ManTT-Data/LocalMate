"""Core configuration for LocalMate v2."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

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
    
    # Google OAuth
    google_client_id: str
    jwt_secret: str

    # MegaLLM (OpenAI-compatible)
    megallm_api_key: str | None = None
    megallm_base_url: str = "https://ai.megallm.io/v1"

    # Optional: CLIP for image embeddings
    huggingface_api_key: str | None = None

    # Default model configs (can be overridden per request)
    default_gemini_model: str = "gemini-2.0-flash"
    default_megallm_model: str = "deepseek-ai/deepseek-v3.1-terminus"
    embedding_model: str = "text-embedding-004"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

