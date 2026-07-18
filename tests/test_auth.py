# -*- coding: utf-8 -*-
"""
🧪 AUTHENTICATION INTEGRATION TESTS (test_auth.py)
-----------------------------------------------
Validates registration, login, and profile retrieval endpoints using pytest fixtures.
"""

import pytest
import httpx
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.core.security import hash_password
from app.models.user import User

# 🧪 Mark all tests as asynchronous
pytestmark = pytest.mark.asyncio


async def test_register_success(client: httpx.AsyncClient, db: AsyncMock):
    """
    🧪 Scenario: Register a new user with a unique email address.
    🔍 Why it matters: This verifies that the registration API endpoint properly validates inputs,
    hashes the password securely, saves the user to the database, and returns a 201 status code.
    """
    # ⚙️ Mock database SELECT returns None indicating email is not registered yet
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    
    # ⚙️ Setup refresh side effect to populate defaults
    def mock_refresh(user):
        user.id = uuid.uuid4()
        user.created_at = datetime.now(timezone.utc)
    db.refresh.side_effect = mock_refresh
    
    payload = {
        "email": "unique_register_test@example.com",
        "password": "strongpassword123",
        "full_name": "Unique Test User"
    }
    
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["email"] == "unique_register_test@example.com"
    assert json_resp["full_name"] == "Unique Test User"
    assert "id" in json_resp
    assert json_resp["is_active"] is True
    
    db.add.assert_called_once()
    db.commit.assert_called_once()


async def test_register_duplicate_email(client: httpx.AsyncClient, db: AsyncMock, auth_user: User):
    """
    🧪 Scenario: Register a user with an email address that is already registered in the system.
    🔍 Why it matters: Prevents users from registering multiple accounts under the same email,
    returning an HTTP 400 Bad Request error to signify a resource conflict.
    """
    # ⚙️ Mock database SELECT returns an existing user record
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = auth_user
    db.execute.return_value = mock_result
    
    payload = {
        "email": auth_user.email,
        "password": "anotherpassword123",
        "full_name": "Duplicate Registration"
    }
    
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


async def test_login_success(client: httpx.AsyncClient, db: AsyncMock, auth_user: User):
    """
    🧪 Scenario: Authenticate user login using correct credentials.
    🔍 Why it matters: Confirms the password verification logic works and that the API issues
    a valid JWT access token with bearer type for subsequent authenticated request routes.
    """
    pwd_plain = "correctpassword123"
    auth_user.hashed_password = hash_password(pwd_plain)
    
    # ⚙️ Mock database user query returned on email search
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = auth_user
    db.execute.return_value = mock_result
    
    payload = {
        "email": auth_user.email,
        "password": pwd_plain
    }
    
    response = await client.post("/auth/login", json=payload)
    
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["token_type"] == "bearer"
    assert "access_token" in json_resp


async def test_login_wrong_password(client: httpx.AsyncClient, db: AsyncMock, auth_user: User):
    """
    🧪 Scenario: Attempt login with incorrect credentials.
    🔍 Why it matters: Verifies authorization restrictions work by rejecting invalid credentials
    and issuing a generic HTTP 401 Unauthorized response to prevent username enumeration.
    """
    auth_user.hashed_password = hash_password("correctpassword123")
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = auth_user
    db.execute.return_value = mock_result
    
    payload = {
        "email": auth_user.email,
        "password": "wrongpassword123"
    }
    
    response = await client.post("/auth/login", json=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


async def test_get_current_user_authenticated(
    client: httpx.AsyncClient,
    db: AsyncMock,
    auth_user: User,
    auth_headers: dict
):
    """
    🧪 Scenario: Request user profile details using a valid JWT token.
    🔍 Why it matters: Confirms current user context injection dependency parses valid tokens,
    looks up user identifiers in the database, and permits secure route actions.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = auth_user
    db.execute.return_value = mock_result
    
    response = await client.get("/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["email"] == auth_user.email
    assert json_resp["full_name"] == auth_user.full_name


async def test_get_current_user_no_token(client: httpx.AsyncClient):
    """
    🧪 Scenario: Attempt profile retrieval request without authorization headers.
    🔍 Why it matters: Ensures router security dependencies block anonymous requests, returning
    an HTTP 401 Unauthorized response automatically.
    """
    response = await client.get("/auth/me")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
