# -*- coding: utf-8 -*-
"""
🔌 DATABASE UTILITIES (database.py)
----------------------------------
Manages asynchronous database connection pooling and sessions for SQLAlchemy.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ⚙️ Create asynchronous engine instance for PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# ⚙️ Configure async session maker
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    # 🗃️ Declarative base class for SQLAlchemy ORM models
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    🔌 Async Dependency Injection Generator for Database Sessions.
    Yields an AsyncSession context that auto-closes at request termination.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
