# -*- coding: utf-8 -*-
"""
⚙️ CONFIGURATION UTILITIES (config.py)
------------------------------------
Loads all application configuration from environment variables or a .env file.

How it works:
  - pydantic-settings reads each field's value from the environment first.
  - If an environment variable is not set, it falls back to the default value.
  - During local development, create a `.env` file in the project root with
    the variables listed below. See `.env.example` for a complete template.
  - In production (e.g. Railway, Docker), set these as real environment variables.

Quick reference — required variables:
  DATABASE_URL              → PostgreSQL async connection string
  SECRET_KEY                → Secret used to sign/verify JWT tokens
  ALGORITHM                 → JWT signature algorithm (default: HS256)
  ACCESS_TOKEN_EXPIRE_MINUTES → JWT validity window in minutes (default: 30)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    ⚙️ Application settings container.

    Inherits from pydantic-settings BaseSettings, which automatically reads
    values from environment variables and the configured .env file.
    Fields are validated by Pydantic at import time — the server will refuse
    to start if a required value is missing or of the wrong type.
    """

    # ⚙️ How pydantic-settings should locate and load the environment file
    model_config = SettingsConfigDict(
        env_file=".env",            # Read from .env in the project root directory
        env_file_encoding="utf-8",  # Encoding of the .env file
        extra="ignore"              # Silently ignore unknown variables in .env
    )

    # 🔌 DATABASE CONNECTION
    # Format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>
    # The asyncpg driver prefix is required for async SQLAlchemy compatibility.
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/taskflow_db",
        description="Asynchronous PostgreSQL connection URL (asyncpg driver)"
    )

    # 🔒 JWT AUTHENTICATION SETTINGS
    # SECRET_KEY: A long random string used to cryptographically sign tokens.
    # ⚠️  The default value is ONLY safe for local development. Change it in production!
    SECRET_KEY: str = Field(
        default="placeholder_secret_key_for_development_purposes_only_change_in_production",
        description="Secret key used for JWT encoding and decoding (keep this private)"
    )

    # ALGORITHM: The signing algorithm. HS256 is HMAC-SHA256 — industry standard.
    ALGORITHM: str = Field(
        default="HS256",
        description="Cryptographic signature algorithm for JWT signing (HS256 = HMAC-SHA256)"
    )

    # ACCESS_TOKEN_EXPIRE_MINUTES: How many minutes a JWT stays valid after issue.
    # After this window expires, the user must log in again to get a fresh token.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Validity duration of JWT access tokens in minutes (default: 30)"
    )

    # 📝 APPLICATION METADATA
    PROJECT_NAME: str = Field(
        default="TaskFlow API",
        description="Human-readable name of the API application (shown in logs and UI)"
    )


# ⚙️ Create a single shared settings instance.
# This is imported by every module that needs configuration access (e.g. database.py, security.py).
# Because Python module imports are cached, this object is created exactly once per process.
settings = Settings()
