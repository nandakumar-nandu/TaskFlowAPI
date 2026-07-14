# -*- coding: utf-8 -*-
"""
🚀 MAIN APPLICATION ENTRYPOINT (main.py)
----------------------------------------
Initializes the FastAPI framework, hooks up middleware, routers, and health checks.
"""

from fastapi import FastAPI, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="TaskFlow API - Simple, secure, and production-ready task management REST API."
)


@app.get("/health")
async def health_check(response: Response, db: AsyncSession = Depends(get_db)):
    """
    🔌 Utility health status check.
    Queries the database using the asynchronous engine to verify active connection.
    """
    try:
        # ⚙️ Run a lightweight validation query
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        # ❌ Connection failure logging and degraded response mapping
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "database": f"disconnected: {str(e)}"
        }
