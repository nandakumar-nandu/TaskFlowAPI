# -*- coding: utf-8 -*-
"""
🧪 TASK CRUD INTEGRATION TESTS (test_tasks.py)
---------------------------------------------
Validates task creation, updates, ownership controls, pagination filters, and deletion.
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
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.category import Category
from app.models.tag import Tag

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


async def test_create_task_success():
    """
    🧪 Test registering a new task: POST /tasks
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    # ⚙️ Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # ⚙️ Setup refresh side effect to populate task details
    def mock_refresh(obj):
        if isinstance(obj, Task):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
            obj.user_id = user.id
            
    mock_db.refresh.side_effect = mock_refresh
    
    task_payload = {
        "title": "Perform Task Scaffolding",
        "description": "Task CRUD endpoints and models implementation.",
        "status": "todo",
        "priority": "high"
    }
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/tasks", json=task_payload, headers=headers)
        
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["title"] == "Perform Task Scaffolding"
    assert json_resp["status"] == "todo"
    assert json_resp["priority"] == "high"
    assert "id" in json_resp
    assert json_resp["user_id"] == str(user.id)
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    app.dependency_overrides.clear()


async def test_get_tasks_list():
    """
    🧪 Test retrieving user task list: GET /tasks
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # ⚙️ Configure database query to return count and tasks list
    task_1 = Task(
        id=uuid.uuid4(),
        title="Task 1",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    task_2 = Task(
        id=uuid.uuid4(),
        title="Task 2",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_count_res = MagicMock()
    mock_count_res.scalar.return_value = 2
    
    mock_tasks_res = MagicMock()
    mock_tasks_res.scalars.return_value.all.return_value = [task_2, task_1]
    
    # ⚙️ Set order of returned objects for execute calls
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # total count query
        mock_count_res,
        # tasks list query
        mock_tasks_res
    ]
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/tasks?limit=5", headers=headers)
        
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["total_count"] == 2
    assert json_resp["limit"] == 5
    assert json_resp["pages"] == 1
    assert len(json_resp["tasks"]) == 2
    assert json_resp["tasks"][0]["title"] == "Task 2"
    
    app.dependency_overrides.clear()


async def test_get_task_by_id_success():
    """
    🧪 Test reading task details by id: GET /tasks/{task_id}
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    task = Task(
        id=uuid.uuid4(),
        title="Specific Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # task details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=task))
    ]
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get(f"/tasks/{task.id}", headers=headers)
        
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Task"
    assert response.json()["user_id"] == str(user.id)
    
    app.dependency_overrides.clear()


async def test_get_task_by_id_forbidden():
    """
    🧪 Test accessing another user's task returns 403 Forbidden: GET /tasks/{task_id}
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    other_user_id = uuid.uuid4()
    task = Task(
        id=uuid.uuid4(),
        title="Secret Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        user_id=other_user_id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # task details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=task))
    ]
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get(f"/tasks/{task.id}", headers=headers)
        
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to access this task"
    
    app.dependency_overrides.clear()


async def test_update_task_success():
    """
    🧪 Test updating a task: PUT /tasks/{task_id}
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    task = Task(
        id=uuid.uuid4(),
        title="Original Title",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # service update task fetch
        MagicMock(scalar_one_or_none=MagicMock(return_value=task))
    ]
    
    update_payload = {
        "title": "Updated Title",
        "status": "in_progress"
    }
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.put(f"/tasks/{task.id}", json=update_payload, headers=headers)
        
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["status"] == "in_progress"
    
    mock_db.commit.assert_called_once()
    app.dependency_overrides.clear()


async def test_delete_task_success():
    """
    🧪 Test deleting a task: DELETE /tasks/{task_id}
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    task = Task(
        id=uuid.uuid4(),
        title="To Delete",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        user_id=user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # service delete task fetch
        MagicMock(scalar_one_or_none=MagicMock(return_value=task))
    ]
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.delete(f"/tasks/{task.id}", headers=headers)
        
    assert response.status_code == 204
    mock_db.delete.assert_called_once_with(task)
    mock_db.commit.assert_called_once()
    
    app.dependency_overrides.clear()


async def test_task_endpoint_security_denied():
    """
    🧪 Test request gets 401 Unauthorized if authorization header is absent.
    """
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/tasks")
        
    assert response.status_code == 401


async def test_create_task_with_category_and_tags():
    """
    🧪 Test registering a new task with category and tags
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    app.dependency_overrides[get_db] = lambda: mock_db
    
    category_id = uuid.uuid4()
    mock_category = Category(id=category_id, name="Work Tasks", user_id=user.id)
    
    # ⚙️ Mock side effects:
    # 1. Fetching current user
    # 2. Category validation check
    # 3. Tag existence search (none exist initially, so resolved as new tags)
    mock_category_result = MagicMock()
    mock_category_result.scalar_one_or_none.return_value = mock_category
    
    mock_tag_result = MagicMock()
    mock_tag_result.scalar_one_or_none.return_value = None  # tag created
    
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        mock_category_result,
        mock_tag_result,
        mock_tag_result
    ]
    
    # Setup database refresh simulation to load relationships
    tag1 = Tag(id=uuid.uuid4(), name="work", user_id=user.id, created_at=datetime.now(timezone.utc))
    tag2 = Tag(id=uuid.uuid4(), name="important", user_id=user.id, created_at=datetime.now(timezone.utc))
    
    def mock_refresh(obj):
        if isinstance(obj, Task):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
            obj.user_id = user.id
            obj.category_id = category_id
            obj.tags = [tag1, tag2]
            
    mock_db.refresh.side_effect = mock_refresh
    
    task_payload = {
        "title": "Task with category and tags",
        "category_id": str(category_id),
        "tags": ["work", "important"]
    }
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/tasks", json=task_payload, headers=headers)
        
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["title"] == "Task with category and tags"
    assert json_resp["category_id"] == str(category_id)
    assert len(json_resp["tags"]) == 2
    assert json_resp["tags"][0]["name"] == "work"
    assert json_resp["tags"][1]["name"] == "important"
    
    app.dependency_overrides.clear()


async def test_get_tasks_with_complex_query():
    """
    🧪 Test retrieving task list with category, tag, sort, order, page, and limit parameters.
    """
    mock_db = AsyncMock(spec=AsyncSession)
    user, headers = setup_auth_context(mock_db)
    app.dependency_overrides[get_db] = lambda: mock_db
    
    category_id = uuid.uuid4()
    task = Task(
        id=uuid.uuid4(),
        title="Filtered Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        category_id=category_id,
        user_id=user.id,
        created_at=datetime.now(timezone.utc),
        tags=[]
    )
    
    mock_count_res = MagicMock()
    mock_count_res.scalar.return_value = 1
    
    mock_tasks_res = MagicMock()
    mock_tasks_res.scalars.return_value.all.return_value = [task]
    
    mock_db.execute.side_effect = [
        # user details query
        MagicMock(scalar_one_or_none=MagicMock(return_value=user)),
        # total count query
        mock_count_res,
        # filtered tasks query
        mock_tasks_res
    ]
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/tasks?status=todo&priority=high&category_id={category_id}&tag=work&page=1&limit=5&sort=due_date&order=asc",
            headers=headers
        )
        
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["total_count"] == 1
    assert json_resp["limit"] == 5
    assert json_resp["offset"] == 0
    assert json_resp["pages"] == 1
    assert len(json_resp["tasks"]) == 1
    assert json_resp["tasks"][0]["title"] == "Filtered Task"
    
    app.dependency_overrides.clear()
