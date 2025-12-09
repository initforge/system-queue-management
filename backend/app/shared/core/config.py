# Core Configuration Settings
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5433/queue_managment"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Queue Management System"
    VERSION: str = "1.0.0"
    
    # CORS
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1", "0.0.0.0"]
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # WebSocket
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    
    # Additional settings to ignore extra env vars
    ENVIRONMENT: Optional[str] = "development"
    DEBUG: Optional[bool] = True
    HOST: Optional[str] = "0.0.0.0"
    PORT: Optional[int] = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()