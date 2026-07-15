# -*- coding: utf-8 -*-
"""
🧪 AUTHENTICATION INTEGRATION TESTS (test_auth.py)
-----------------------------------------------
Validates registration, login, and profile retrieval endpoints.
"""

import pytest
import httpx
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User

# 🧪 Mark all tests as asynchronous
pytestmark = pytest.mark.asyncio


async def test_register_user_success():
    """
    🧪 Test registration success: POST /auth/register
    """
    mock_db = AsyncMock(spec=AsyncSession)
    
    # ⚙️ Mock database SELECT returns None (email is unique)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # ⚙️ Mock refresh side-effect to populate default UUID and timestamp
    def mock_refresh(user):
        user.id = uuid.uuid4()
        user.created_at = datetime.now(timezone.utc)
    mock_db.refresh.side_effect = mock_refresh
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    register_payload = {
        "email": "register_test@example.com",
        "password": "securepassword123",
        "full_name": "Test Registration"
    }
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/auth/register", json=register_payload)
        
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["email"] == "register_test@example.com"
    assert json_resp["full_name"] == "Test Registration"
    assert "id" in json_resp
    assert json_resp["is_active"] is True
    
    # 🧪 Validate database insert execution calls
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    
    app.dependency_overrides.clear()


async def test_register_user_conflict():
    """
    🧪 Test registration conflict when email is already registered.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    
    # ⚙️ Mock database SELECT returns an existing User object
    existing_user = User(
        id=uuid.uuid4(),
        email="conflict@example.com",
        hashed_password="hashed_dummy_password",
        created_at=datetime.now(timezone.utc),
        is_active=True
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    register_payload = {
        "email": "conflict@example.com",
        "password": "securepassword123",
        "full_name": "Conflict Registration"
    }
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/auth/register", json=register_payload)
        
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
    
    app.dependency_overrides.clear()


async def test_login_success():
    """
    🧪 Test login success: POST /auth/login returns JWT access token
    """
    mock_db = AsyncMock(spec=AsyncSession)
    
    # ⚙️ Hash password and mock the returned database user
    pwd_plain = "loginpassword123"
    pwd_hashed = hash_password(pwd_plain)
    user_in_db = User(
        id=uuid.uuid4(),
        email="login_test@example.com",
        hashed_password=pwd_hashed,
        created_at=datetime.now(timezone.utc),
        is_active=True
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_in_db
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    login_payload = {
        "email": "login_test@example.com",
        "password": pwd_plain
    }
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/auth/login", json=login_payload)
        
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["token_type"] == "bearer"
    assert "access_token" in json_resp
    
    app.dependency_overrides.clear()


async def test_login_invalid_credentials():
    """
    🧪 Test login rejection for invalid password credentials.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    
    # ⚙️ Mock database user with a different hashed password
    user_in_db = User(
        id=uuid.uuid4(),
        email="login_fail@example.com",
        hashed_password=hash_password("correctpassword"),
        created_at=datetime.now(timezone.utc),
        is_active=True
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_in_db
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    login_payload = {
        "email": "login_fail@example.com",
        "password": "wrongpassword"
    }
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/auth/login", json=login_payload)
        
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
    
    app.dependency_overrides.clear()


async def test_get_current_user_profile():
    """
    🧪 Test profile retrieval with valid JWT token: GET /auth/me
    """
    mock_db = AsyncMock(spec=AsyncSession)
    
    # ⚙️ Mock database returned user matching JWT subject ID
    user_in_db = User(
        id=uuid.uuid4(),
        email="me_test@example.com",
        full_name="Me Profile",
        created_at=datetime.now(timezone.utc),
        is_active=True
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_in_db
    mock_db.execute.return_value = mock_result
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # ⚙️ Generate valid JWT token for the user ID
    token = create_access_token(data={"sub": str(user_in_db.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/auth/me", headers=headers)
        
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["email"] == "me_test@example.com"
    assert json_resp["full_name"] == "Me Profile"
    
    app.dependency_overrides.clear()
