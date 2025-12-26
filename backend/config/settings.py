"""Application configuration settings."""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using pydantic-settings."""
    
    # API Configuration
    API_TITLE: str = "TopHub Article API"
    API_DESCRIPTION: str = "API for TopHub article management and analysis"
    API_VERSION: str = "1.0.0"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Elasticsearch Configuration
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_INDEX: str = "tophub_articles"
    ELASTICSEARCH_USER: str = ""
    ELASTICSEARCH_PASSWORD: str = ""
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Request Configuration
    REQUEST_TIMEOUT: int = 30  # seconds
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env file


# Global settings instance
settings = Settings()
