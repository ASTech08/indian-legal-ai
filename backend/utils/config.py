from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Indian Legal AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/legal_ai"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_EXPIRE: int = 3600  # 1 hour
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    
    # Vector Store
    CHROMADB_PATH: str = "./data/chromadb"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # File Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = "indian-legal-ai"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "doc", "txt", "jpg", "jpeg", "png"]
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://indian-legal-ai.vercel.app"
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Legal Data Sources
    INDIANKANOON_BASE_URL: str = "https://indiankanoon.org"
    ECOURTS_BASE_URL: str = "https://ecourts.gov.in"
    INDIACODE_BASE_URL: str = "https://www.indiacode.nic.in"
    
    # AI Training
    TRAINING_DATA_PATH: str = "./data/training"
    MODELS_PATH: str = "./models"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Sentry (Error Tracking)
    SENTRY_DSN: str = ""
    
    # Email (for notifications)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
