from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://neondb_owner:npg_RakbDZKPwm72@ep-little-breeze-apbenx3x-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    APP_NAME: str = "Inventory Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS — override via ALLOWED_ORIGINS env var (comma-separated) on Render
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://frontend:3000",
        # Render deployments
        "https://inventory-assignment-frontend.onrender.com",
        "https://inventory-assignment-backend.onrender.com",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

