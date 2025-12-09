# Core Configuration Settings
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://admin:password@db:5432/queue_managment"
    
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
    ALLOWED_HOSTS: list = ["*"]
    CORS_ORIGINS: Optional[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # WebSocket
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    
    # Additional settings to ignore extra env vars
    ENVIRONMENT: Optional[str] = "development"
    DEBUG: Optional[bool] = True
    HOST: Optional[str] = "0.0.0.0"
    PORT: Optional[int] = 8000
    
    # Gemini AI Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "AlzaSyBS33D0yduetuAkIMPhfL4CFA_4hYkfd3g")
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: Optional[str] = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: Optional[str] = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: Optional[str] = os.getenv("CLOUDINARY_API_SECRET", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()