# -*- coding: utf-8 -*-
"""
🧪 TASK CRUD INTEGRATION TESTS (test_tasks.py)
---------------------------------------------
Validates task creation, updates, ownership controls, pagination filters, and deletion using pytest fixtures.
"""

import pytest
import httpx
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.category import Category
from app.models.tag import Tag

# 🧪 Mark all tests as asynchronous
pytestmark = pytest.mark.asyncio


def mock_current_user_inject(db: AsyncMock, auth_user: User):
    """
    ⚙️ Helper to mock current user profile lookup during JWT validation.
    """
    mock_user_res = MagicMock()
    mock_user_res.scalar_one_or_none.return_value = auth_user
    db.execute.return_value = mock_user_res


async def test_create_task(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """Create a new task with basic parameters."""
    mock_current_user_inject(db, auth_user)
    
    # ⚙️ Mock refresh side-effect to populate default UUID and timestamp
    def mock_refresh(obj):
        if isinstance(obj, Task):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
            obj.user_id = auth_user.id
            
    db.refresh.side_effect = mock_refresh
    
    payload = {
        "title": "Basic Task Title",
        "description": "Basic Task Description",
        "status": "todo",
        "priority": "medium"
    }
    
    response = await client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["title"] == "Basic Task Title"
    assert json_resp["status"] == "todo"
    assert "id" in json_resp
    assert json_resp["user_id"] == str(auth_user.id)
    
    assert db.add.called
    db.commit.assert_called_once()


async def test_get_tasks_pagination(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """Retrieve user tasks with paging parameters: limit and page."""
    mock_current_user_inject(db, auth_user)
    
    task_1 = Task(
        id=uuid.uuid4(),
        title="First Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        user_id=auth_user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_count_res = MagicMock()
    mock_count_res.scalar.return_value = 1
    
    mock_tasks_res = MagicMock()
    mock_tasks_res.scalars.return_value.all.return_value = [task_1]
    
    # Setup execution results: user fetch, total count query, tasks list query
    db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=auth_user)),
        mock_count_res,
        mock_tasks_res
    ]
    
    response = await client.get("/api/v1/tasks?page=2&limit=5", headers=auth_headers)
    
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["total_count"] == 1
    assert json_resp["limit"] == 5
    assert json_resp["offset"] == 5  # (page - 1) * limit => (2 - 1) * 5 = 5
    assert json_resp["pages"] == 1
    assert len(json_resp["tasks"]) == 1
    assert json_resp["tasks"][0]["title"] == "First Task"


async def test_update_task_own(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """Update a task owned by the requesting authenticated user."""
    mock_current_user_inject(db, auth_user)
    
    task = Task(
        id=uuid.uuid4(),
        title="Original Task Name",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        user_id=auth_user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    # Execution: user fetch, then task fetch inside update_task service
    db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=auth_user)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=task))
    ]
    
    payload = {
        "title": "New Updated Name",
        "status": "in_progress"
    }
    
    response = await client.put(f"/api/v1/tasks/{task.id}", json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["title"] == "New Updated Name"
    assert json_resp["status"] == "in_progress"
    
    db.commit.assert_called_once()


async def test_delete_task_own(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """Delete a task owned by the requesting authenticated user."""
    mock_current_user_inject(db, auth_user)
    
    task = Task(
        id=uuid.uuid4(),
        title="Task to delete",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        user_id=auth_user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=auth_user)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=task))
    ]
    
    response = await client.delete(f"/api/v1/tasks/{task.id}", headers=auth_headers)
    
    assert response.status_code == 204
    db.delete.assert_called_once_with(task)
    db.commit.assert_called_once()


async def test_access_other_user_task(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """Attempt to read details of a task belonging to a different user: GET /tasks/{task_id}."""
    mock_current_user_inject(db, auth_user)
    
    other_user_id = uuid.uuid4()
    task = Task(
        id=uuid.uuid4(),
        title="Another User Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        user_id=other_user_id,
        created_at=datetime.now(timezone.utc)
    )
    
    db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=auth_user)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=task))
    ]
    
    response = await client.get(f"/api/v1/tasks/{task.id}", headers=auth_headers)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to access this task"


async def test_filter_by_status(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """Filter tasks list querying specifically by execution status."""
    mock_current_user_inject(db, auth_user)
    
    task = Task(
        id=uuid.uuid4(),
        title="Done Task",
        status=TaskStatus.DONE,
        priority=TaskPriority.MEDIUM,
        user_id=auth_user.id,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_count_res = MagicMock()
    mock_count_res.scalar.return_value = 1
    
    mock_tasks_res = MagicMock()
    mock_tasks_res.scalars.return_value.all.return_value = [task]
    
    db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=auth_user)),
        mock_count_res,
        mock_tasks_res
    ]
    
    response = await client.get("/api/v1/tasks?status=done", headers=auth_headers)
    
    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp["tasks"]) == 1
    assert json_resp["tasks"][0]["status"] == "done"


# 🧪 Additional integration tests verifying Commit 4 Category & Tag functionality

async def test_create_task_with_category_and_tags(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """Register a new task linked with category_id and inline tag string arrays."""
    mock_current_user_inject(db, auth_user)
    
    category_id = uuid.uuid4()
    mock_category = Category(id=category_id, name="Work Tasks", user_id=auth_user.id)
    
    mock_category_result = MagicMock()
    mock_category_result.scalar_one_or_none.return_value = mock_category
    
    mock_tag_result = MagicMock()
    mock_tag_result.scalar_one_or_none.return_value = None  # means new tags will be created
    
    db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=auth_user)),
        mock_category_result,
        mock_tag_result,
        mock_tag_result
    ]
    
    tag1 = Tag(id=uuid.uuid4(), name="work", user_id=auth_user.id, created_at=datetime.now(timezone.utc))
    tag2 = Tag(id=uuid.uuid4(), name="important", user_id=auth_user.id, created_at=datetime.now(timezone.utc))
    
    def mock_refresh(obj):
        if isinstance(obj, Task):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
            obj.user_id = auth_user.id
            obj.category_id = category_id
            obj.tags = [tag1, tag2]
            
    db.refresh.side_effect = mock_refresh
    
    task_payload = {
        "title": "Task with category and tags",
        "category_id": str(category_id),
        "tags": ["work", "important"]
    }
    
    response = await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["title"] == "Task with category and tags"
    assert json_resp["category_id"] == str(category_id)
    assert len(json_resp["tags"]) == 2
    assert json_resp["tags"][0]["name"] == "work"
    assert json_resp["tags"][1]["name"] == "important"


async def test_get_tasks_with_complex_query(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """Retrieve filtered, sorted, and paginated tasks under multiple filters simultaneously."""
    mock_current_user_inject(db, auth_user)
    
    category_id = uuid.uuid4()
    task = Task(
        id=uuid.uuid4(),
        title="Filtered Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        category_id=category_id,
        user_id=auth_user.id,
        created_at=datetime.now(timezone.utc),
        tags=[]
    )
    
    mock_count_res = MagicMock()
    mock_count_res.scalar.return_value = 1
    
    mock_tasks_res = MagicMock()
    mock_tasks_res.scalars.return_value.all.return_value = [task]
    
    db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=auth_user)),
        mock_count_res,
        mock_tasks_res
    ]
    
    response = await client.get(
        f"/api/v1/tasks?status=todo&priority=high&category_id={category_id}&tag=work&page=1&limit=5&sort=due_date&order=asc",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["total_count"] == 1
    assert json_resp["limit"] == 5
    assert json_resp["offset"] == 0
    assert json_resp["pages"] == 1
    assert len(json_resp["tasks"]) == 1
    assert json_resp["tasks"][0]["title"] == "Filtered Task"
