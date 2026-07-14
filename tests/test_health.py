# -*- coding: utf-8 -*-
"""
🧪 HEALTH CHECK ENDPOINT TESTS (test_health.py)
---------------------------------------------
Test suite for validating the FastAPI health check endpoint under different conditions.
"""

import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from app.main import app
from app.core.database import get_db

# 🧪 Mark all tests in this module as asynchronous
pytestmark = pytest.mark.asyncio


async def test_health_check_success():
    """
    🧪 Test GET /health returns 200 OK when the database connects successfully.
    """
    # 🔌 Create a mock async session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # ⚙️ Setup dependency override to return the mock session
    app.dependency_overrides[get_db] = lambda: mock_db
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/health")
        
    # 🧪 Validate database query execution
    mock_db.execute.assert_called_once()
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "connected"
    }
    
    # ⚙️ Reset dependency overrides
    app.dependency_overrides.clear()


async def test_health_check_database_error():
    """
    🧪 Test GET /health returns 503 Service Unavailable when the database is offline.
    """
    # 🔌 Create a mock async session that throws an error when queried
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = Exception("Connection refused by host")
    
    # ⚙️ Setup dependency override to return the mock session
    app.dependency_overrides[get_db] = lambda: mock_db
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/health")
        
    assert response.status_code == 503
    assert response.json()["status"] == "error"
    assert "disconnected: Connection refused by host" in response.json()["database"]
    
    # ⚙️ Reset dependency overrides
    app.dependency_overrides.clear()
