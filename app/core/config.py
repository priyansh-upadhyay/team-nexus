from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = Field("Team Task Manager", env="APP_NAME")
    APP_VERSION: str = Field("0.1.0", env="APP_VERSION")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DATABASE_URL: str
    # JWT Configuration
    SECRET_KEY: str = Field("your-secret-key-change-this-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Authentication
    BCRYPT_ROUNDS: int = Field(12, env="BCRYPT_ROUNDS")

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = Field([], env="BACKEND_CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()
