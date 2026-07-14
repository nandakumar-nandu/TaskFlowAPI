# -*- coding: utf-8 -*-
"""
⚙️ CONFIGURATION UTILITIES (config.py)
------------------------------------
Defines and loads config settings for the TaskFlow API using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # 📝 Configuration settings for local environment variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 🔌 Database Connection URL (Asyncpg PostgreSQL)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/taskflow_db",
        description="Asynchronous PostgreSQL connection URL"
    )

    # 🔒 JWT Authentication Configuration
    SECRET_KEY: str = Field(
        default="placeholder_secret_key_for_development_purposes_only_change_in_production",
        description="Secret key for JWT encoding and decoding"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="Signature algorithm for JWT signing"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Validity duration of JWT tokens in minutes"
    )

    # 📝 Project Meta
    PROJECT_NAME: str = Field(
        default="TaskFlow API",
        description="Name of the API application"
    )


# ⚙️ Instantiate settings object to load configurations globally
settings = Settings()
