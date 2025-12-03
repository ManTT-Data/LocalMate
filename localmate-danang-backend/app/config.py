"""
Global Application Settings

Đọc các biến môi trường và cung cấp settings cho toàn bộ ứng dụng
"""

import enum
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, enum.Enum):
    """Log level enum"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "change-me-in-production"

    # Database
    POSTGRES_URL: str = "postgresql+asyncpg://user:password@localhost:5432/localmate"

    # Supabase (optional)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Neo4j Graph Database
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Vector Database
    VECTOR_DB_URL: str = ""
    VECTOR_DB_API_KEY: str = ""

    # LLM Providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Vision API
    CLIP_MODEL_PATH: str = "ViT-B/32"
    VISION_API_KEY: str = ""

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"

    # MCP Tools - Grab
    GRAB_API_KEY: str = ""
    GRAB_API_SECRET: str = ""
    GRAB_WEBHOOK_SECRET: str = ""

    # MCP Tools - Hotel Booking
    AGODA_API_KEY: str = ""
    KLOOK_API_KEY: str = ""

    # MCP Tools - Weather
    WEATHER_API_KEY: str = ""

    # MCP Tools - Social Crawler
    FACEBOOK_ACCESS_TOKEN: str = ""
    GOOGLE_PLACES_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Logging
    LOG_LEVEL: LogLevel = LogLevel.INFO


# Create global settings instance
settings = Settings()
