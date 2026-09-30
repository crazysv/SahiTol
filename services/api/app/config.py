"""Application configuration settings using Pydantic Settings."""
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "SahiTol API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database connection
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://sahitol:sahitol_secret@localhost:5432/sahitol_db",
        description="Database URL for application connections"
    )
    MIGRATION_DATABASE_URL: str = Field(
        default="postgresql+psycopg://sahitol:sahitol_secret@localhost:5432/sahitol_db",
        description="Database URL for running schema migrations"
    )

    # JWT Authentication & PIN Security
    JWT_SECRET_KEY: str = Field(
        default="dev-jwt-secret-key-change-in-production-minimum-32-chars!",
        description="Secret key for JWT token signing"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PIN_PEPPER: str = "dev-pin-pepper-minimum-16-bytes"

    # Storage Backend
    STORAGE_BACKEND: str = Field(default="local", description="'local' or 'supabase'")
    LOCAL_MEDIA_ROOT: str = "./media_storage"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "sahitol-media"

    # Network / CORS / Public URLs
    PUBLIC_API_BASE_URL: str = "http://localhost:8000"
    PUBLIC_WEB_BASE_URL: str = "http://localhost:5173"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return list(v)
        return v

    # Isolated Demo Support
    DEMO_MODE: bool = True
    DEMO_TENANT_ID: str = "demo-tenant-0001"


settings = Settings()
