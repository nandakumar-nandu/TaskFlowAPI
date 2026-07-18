# -*- coding: utf-8 -*-
"""
⚙️ PYTEST TEST FIXTURES CONFIGURATION (conftest.py)
--------------------------------------------------
Defines shared database and API client fixtures for the FastAPI integration test suite.

Pytest Fixture Scopes Explanation:
Fixtures are created by decorators and run depending on their configured scope:
1. 'function' (default): Runs once for each test function. Best for isolating state between individual test runs (e.g. database transactions or mocks).
2. 'class': Runs once for each test class. Useful when multiple test methods share heavier setup steps.
3. 'module': Runs once per test file/module. Good for setting up file-level configurations or read-only states.
4. 'package': Runs once per package folder.
5. 'session': Runs once for the entire pytest session execution lifecycle. Best for global setups like database container migrations or webservers.
"""

import pytest
import httpx
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User


@pytest.fixture(scope="function")
def db() -> AsyncMock:
    """
    ⚙️ Pytest fixture to provide a mocked SQLAlchemy AsyncSession.
    Scope: function (runs for every test function individually to ensure database mock state separation).
    """
    mock_db = AsyncMock(spec=AsyncSession)
    return mock_db


@pytest.fixture(scope="function")
async def client(db: AsyncMock) -> httpx.AsyncClient:
    """
    ⚙️ Pytest fixture providing an HTTPX AsyncClient configured with FastAPI app and mocked db override.
    Scope: function (individual request context isolation).
    """
    # Override database dependency injection
    app.dependency_overrides[get_db] = lambda: db
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    # Clean up override dependency after test runs
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_user() -> User:
    """
    ⚙️ Pytest fixture to instantiate a mock user profile.
    Scope: function (returns a new User object instance).
    """
    return User(
        id=uuid.uuid4(),
        email="test_user@example.com",
        full_name="Test User",
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )


@pytest.fixture(scope="function")
def auth_headers(auth_user: User) -> dict:
    """
    ⚙️ Pytest fixture that creates valid JWT authorization headers matching the auth_user fixture.
    Scope: function.
    """
    token = create_access_token(data={"sub": str(auth_user.id)})
    return {"Authorization": f"Bearer {token}"}
