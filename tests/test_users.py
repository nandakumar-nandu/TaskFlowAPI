# -*- coding: utf-8 -*-
"""
🧪 USER PROFILE INTEGRATION TESTS (test_users.py)
-----------------------------------------------
Validates retrieval, partial updates, and avatar uploads for user profiles.
"""

import pytest
import httpx
import uuid
import io
import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User

# 🧪 Mark all tests as asynchronous
pytestmark = pytest.mark.asyncio


def setup_auth_context(mock_db):
    """
    ⚙️ Helper utility to configure mock authenticated user context
    """
    user = User(
        id=uuid.uuid4(),
        email="test_profile@example.com",
        full_name="Profile Tester",
        is_active=True,
        avatar_url=None,
        created_at=datetime.now(timezone.utc)
    )
    
    token = create_access_token(data={"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_result.scalar_one.return_value = user
    mock_db.execute.return_value = mock_result
    
    return user, headers


async def test_get_my_profile():
    """
    🧪 Scenario: Retrieve the authenticated user's own profile data.
    🔍 Why it matters: Ensures that the `/users/me` endpoint correctly extracts
    the user's identity from the JWT token and returns their profile without exposing others.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/users/me", headers=headers)
        
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["email"] == "test_profile@example.com"
    assert json_resp["full_name"] == "Profile Tester"
    
    app.dependency_overrides.clear()


async def test_update_full_name():
    """
    🧪 Scenario: Partially update the authenticated user's profile (e.g., full_name).
    🔍 Why it matters: Validates the PATCH logic that updates only the provided fields,
    leaving other fields (like email and password) intact and uncorrupted.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    update_payload = {"full_name": "New Display Name"}
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.patch("/users/me", json=update_payload, headers=headers)
        
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["full_name"] == "New Display Name"
    assert json_resp["email"] == "test_profile@example.com"
    
    mock_db.commit.assert_called_once()
    app.dependency_overrides.clear()


async def test_upload_avatar_valid():
    """
    🧪 Scenario: Upload a valid PNG avatar image.
    🔍 Why it matters: Confirms that the multipart/form-data upload works, the file is
    saved securely, and the `avatar_url` is updated in the database.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    file_content = b"fake png file content"
    files = {"file": ("avatar.png", io.BytesIO(file_content), "image/png")}
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/users/me/avatar", files=files, headers=headers)
        
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["avatar_url"] is not None
    assert json_resp["avatar_url"].endswith(".png")
    
    mock_db.commit.assert_called_once()
    app.dependency_overrides.clear()
    
    # 🧹 Clean up the created physical media file to keep repository clean
    local_filename = f"media/avatars/{user.id}.png"
    if os.path.exists(local_filename):
        os.remove(local_filename)


async def test_upload_avatar_invalid_type():
    """
    🧪 Scenario: Attempt to upload an unsupported file format (e.g., PDF) as an avatar.
    🔍 Why it matters: Verifies the security middleware and route logic block invalid
    content types to prevent injection or storage abuse, returning HTTP 415.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    files = {"file": ("document.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")}
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/users/me/avatar", files=files, headers=headers)
        
    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported media type. Only image/jpeg, image/png, and image/webp are accepted."
    
    app.dependency_overrides.clear()
