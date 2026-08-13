# -*- coding: utf-8 -*-
"""
🧪 TASK ACTIVITY INTEGRATION TESTS (test_activity.py)
-----------------------------------------------------
Validates creation logging, diff snapshot capture during updates, and activity authorization rules.
"""

import pytest
import httpx
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.activity import TaskActivity

# 🧪 Mark all tests as asynchronous
pytestmark = pytest.mark.asyncio


async def test_create_logs_activity(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """
    🧪 Scenario: Trigger a task creation event to verify activity logging.
    🔍 Why it matters: Ensures that when a task is created, a corresponding
    `task.created` entry is generated in the audit log in the same transaction.
    """
    task_payload = {"title": "Task to audit"}
    
    # ⚙️ Mock queries for user lookup
    def mock_execute(query):
        query_str = str(query)
        mock_res = MagicMock()
        if "FROM users" in query_str or "users.id" in query_str:
            mock_res.scalar_one_or_none.return_value = auth_user
            mock_res.scalar_one.return_value = auth_user
        return mock_res
        
    db.execute.side_effect = mock_execute
    
    logged_activities = []
    
    def mock_add(obj):
        if isinstance(obj, TaskActivity):
            logged_activities.append(obj)
            
    db.add.side_effect = mock_add
    
    def mock_refresh(obj):
        if isinstance(obj, Task):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
    db.refresh.side_effect = mock_refresh
    
    response = await client.post("/tasks", json=task_payload, headers=auth_headers)
    
    assert response.status_code == 201
    assert len(logged_activities) == 1
    assert logged_activities[0].action == "task.created"
    assert logged_activities[0].user_id == auth_user.id
    assert logged_activities[0].diff is None


async def test_update_logs_diff(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """
    🧪 Scenario: Modify a task's status and check the generated diff payload.
    🔍 Why it matters: Validates the diff calculation logic. A `task.updated` entry
    must include a JSON diff showing the `before` and `after` states of modified fields.
    """
    task_id = uuid.uuid4()
    task = Task(
        id=task_id,
        user_id=auth_user.id,
        title="Existing Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        created_at=datetime.now(timezone.utc)
    )
    
    def mock_execute(query):
        query_str = str(query)
        mock_res = MagicMock()
        if "FROM users" in query_str or "users.id" in query_str:
            mock_res.scalar_one_or_none.return_value = auth_user
            mock_res.scalar_one.return_value = auth_user
        elif "FROM tasks" in query_str or "tasks.id" in query_str:
            mock_res.scalar_one_or_none.return_value = task
            mock_res.scalar_one.return_value = task
        return mock_res
        
    db.execute.side_effect = mock_execute
    
    logged_activities = []
    
    def mock_add(obj):
        if isinstance(obj, TaskActivity):
            logged_activities.append(obj)
            
    db.add.side_effect = mock_add
    
    def mock_refresh(obj):
        pass
    db.refresh.side_effect = mock_refresh
    
    update_payload = {"status": "done"}
    
    response = await client.put(f"/tasks/{task_id}", json=update_payload, headers=auth_headers)
    
    assert response.status_code == 200
    assert len(logged_activities) == 1
    assert logged_activities[0].action == "task.updated"
    assert logged_activities[0].diff is not None
    assert "status" in logged_activities[0].diff
    assert logged_activities[0].diff["status"]["before"] == "todo"
    assert logged_activities[0].diff["status"]["after"] == "done"


async def test_activity_forbidden_for_other_user(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """
    🧪 Scenario: Attempt to view the activity audit log of a task owned by someone else.
    🔍 Why it matters: Protects sensitive audit trails. Only the task owner should
    be able to view the history of their task, returning HTTP 403 for unauthorized access.
    """
    task_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    task = Task(
        id=task_id,
        user_id=other_user_id,
        title="Other user's task"
    )
    
    def mock_execute(query):
        query_str = str(query)
        mock_res = MagicMock()
        if "FROM users" in query_str or "users.id" in query_str:
            mock_res.scalar_one_or_none.return_value = auth_user
            mock_res.scalar_one.return_value = auth_user
        elif "FROM tasks" in query_str or "tasks.id" in query_str:
            mock_res.scalar_one_or_none.return_value = task
            mock_res.scalar_one.return_value = task
        return mock_res
        
    db.execute.side_effect = mock_execute
    
    response = await client.get(f"/tasks/{task_id}/activity", headers=auth_headers)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to access this task activity"
