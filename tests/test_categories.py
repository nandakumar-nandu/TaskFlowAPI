# -*- coding: utf-8 -*-
"""
🧪 CATEGORY CRUD INTEGRATION TESTS (test_categories.py)
-----------------------------------------------------
Validates category creation, retrieval, updates, deletion, and strict ownership restrictions.
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
from app.models.category import Category

# 🧪 Mark all tests as asynchronous
pytestmark = pytest.mark.asyncio


def setup_auth_context(mock_db):
    """
    ⚙️ Helper utility to configure mock user and headers context
    """
    user = User(
        id=uuid.uuid4(),
        email="test_user@example.com",
        full_name="Test User",
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    
    # 🔒 Mock JWT token authentication
    token = create_access_token(data={"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    # ⚙️ Mock default select behavior for token authentication user fetch
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_db.execute.return_value = mock_result
    
    return user, headers


async def test_create_category_success():
    """Registering a new category: POST /categories."""
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    # ⚙️ Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # ⚙️ Setup refresh side effect to populate category details
    def mock_refresh(obj):
        if isinstance(obj, Category):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
            obj.user_id = user.id
            
    mock_db.refresh.side_effect = mock_refresh
    
    category_payload = {
        "name": "Work Tasks"
    }
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/api/v1/categories", json=category_payload, headers=headers)
        
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["name"] == "Work Tasks"
    assert "id" in json_resp
    assert json_resp["user_id"] == str(user.id)
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    app.dependency_overrides.clear()


async def test_get_categories_list():
    """Retrieving user category list: GET /categories."""
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    cat1 = Category(
        id=uuid.uuid4(),
        name="Personal",
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    cat2 = Category(
        id=uuid.uuid4(),
        name="Work",
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [cat1, cat2]
    
    # Set execute call sequence
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # categories query
        mock_result
    ]
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/categories", headers=headers)
        
    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp) == 2
    assert json_resp[0]["name"] == "Personal"
    assert json_resp[1]["name"] == "Work"
    
    app.dependency_overrides.clear()


async def test_get_category_by_id_success():
    """Reading category details by id: GET /categories/{category_id}."""
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    cat = Category(
        id=uuid.uuid4(),
        name="Urgent Tasks",
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # category details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=cat))
    ]
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get(f"/api/v1/categories/{cat.id}", headers=headers)
        
    assert response.status_code == 200
    assert response.json()["name"] == "Urgent Tasks"
    assert response.json()["user_id"] == str(user.id)
    
    app.dependency_overrides.clear()


async def test_get_category_by_id_forbidden():
    """Accessing another user's category returns 403 Forbidden: GET /categories/{category_id}."""
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    other_user_id = uuid.uuid4()
    cat = Category(
        id=uuid.uuid4(),
        name="Private Category",
        user_id=other_user_id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # category details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=cat))
    ]
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get(f"/api/v1/categories/{cat.id}", headers=headers)
        
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to access this category"
    
    app.dependency_overrides.clear()


async def test_update_category_success():
    """Updating a category: PUT /categories/{category_id}."""
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    cat = Category(
        id=uuid.uuid4(),
        name="Old Name",
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # category fetch inside service update
        MagicMock(scalar_one_or_none=MagicMock(return_value=cat))
    ]
    
    update_payload = {
        "name": "New Name"
    }
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.put(f"/api/v1/categories/{cat.id}", json=update_payload, headers=headers)
        
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    
    mock_db.commit.assert_called_once()
    app.dependency_overrides.clear()


async def test_delete_category_success():
    """Deleting a category: DELETE /categories/{category_id}."""
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    cat = Category(
        id=uuid.uuid4(),
        name="To Delete",
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=cat)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=cat)),
        MagicMock(),
        MagicMock()
    ]
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.delete(f"/api/v1/categories/{cat.id}", headers=headers)
        
    assert response.status_code == 204
    
    app.dependency_overrides.clear()
