# -*- coding: utf-8 -*-
"""
🔌 DATABASE UTILITIES (database.py)
------------------------------------
Sets up the asynchronous database engine, session factory, declarative base,
and the FastAPI dependency that provides a fresh database session per request.

Key concepts for beginners:
  - SQLAlchemy ORM: A library that lets you interact with the database using
    Python classes instead of writing raw SQL queries.
  - AsyncSession: An async-compatible session that runs queries without blocking
    the server event loop (critical for a high-concurrency async API).
  - Dependency Injection (get_db): FastAPI automatically calls `get_db` and
    passes the session to any route function that declares it with Depends(get_db).
  - DeclarativeBase (Base): All ORM model classes (User, Task, etc.) inherit
    from `Base`. SQLAlchemy uses this shared base to track all known tables.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ⚙️ ASYNC DATABASE ENGINE
# create_async_engine builds the connection pool that talks to PostgreSQL.
# Options explained:
#   settings.DATABASE_URL → connection string from config (postgresql+asyncpg://...)
#   echo=False            → set True in development to print all SQL statements to stdout
#   future=True           → opt-in to SQLAlchemy 2.0 behaviour (more predictable)
#   pool_pre_ping=True    → test each connection before using it (auto-reconnects stale connections)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# ⚙️ ASYNC SESSION FACTORY
# async_sessionmaker is a factory that creates AsyncSession objects on demand.
# Options explained:
#   bind=engine           → sessions produced by this factory use our engine
#   class_=AsyncSession   → produce async-compatible session instances
#   expire_on_commit=False → keep ORM objects usable after commit (avoids lazy-load errors)
#   autocommit=False      → transactions must be committed manually (safer, explicit)
#   autoflush=False       → don't auto-flush pending changes before every query (we control this)
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """
    🗃️ Declarative ORM base class.

    All SQLAlchemy model classes (User, Task, Category, etc.) must inherit
    from this Base so SQLAlchemy knows about every table in the schema.
    Alembic also reads from Base.metadata when generating migration scripts.
    """
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    🔌 FastAPI dependency that yields a database session per request.

    This is an async generator function decorated as a FastAPI dependency.
    FastAPI calls it automatically for any route handler that declares:
        db: AsyncSession = Depends(get_db)

    Lifecycle:
        1. Open a new AsyncSession via the session factory.
        2. Yield it to the route handler (the route runs here).
        3. When the route finishes (or raises an exception), close the session
           in the finally block to return the connection to the pool.

    The `async with` context manager handles the session lifecycle. The
    `finally` clause guarantees the session is always closed — even on errors —
    preventing connection pool exhaustion.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            # ⚙️ Always close the session after the request completes.
            # This releases the underlying database connection back to the pool.
            await session.close()
