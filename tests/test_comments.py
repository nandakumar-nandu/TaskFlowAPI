# -*- coding: utf-8 -*-
"""
🧪 TASK COMMENTS INTEGRATION TESTS (test_comments.py)
--------------------------------------------------
Validates nesting comment listing, creation, updating, and authorization checks.
"""

import pytest
import httpx
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.models.user import User
from app.models.task import Task
from app.models.comment import Comment

# 🧪 Mark all tests as asynchronous
pytestmark = pytest.mark.asyncio


async def test_create_comment(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """
    user can post a comment on their own task
    """
    task_id = uuid.uuid4()
    task = Task(id=task_id, user_id=auth_user.id, title="Test Task")
    
    # ⚙️ Mock queries for user lookup and task ownership verification
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
    
    def mock_refresh(obj):
        if isinstance(obj, Comment):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = None
    db.refresh.side_effect = mock_refresh
    
    payload = {"body": "This is a valid task comment."}
    
    response = await client.post(f"/tasks/{task_id}/comments", json=payload, headers=auth_headers)
    
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["body"] == "This is a valid task comment."
    assert json_resp["task_id"] == str(task_id)
    assert json_resp["user_id"] == str(auth_user.id)
    db.commit.assert_called_once()


async def test_list_comments_ordered(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """
    list returns all comments in
    created_at ascending order
    """
    task_id = uuid.uuid4()
    task = Task(id=task_id, user_id=auth_user.id, title="Test Task")
    
    # Create two comments with distinct creation times
    comment1 = Comment(
        id=uuid.uuid4(),
        task_id=task_id,
        user_id=auth_user.id,
        body="First comment",
        created_at=datetime(2026, 7, 25, 10, 0, 0, tzinfo=timezone.utc)
    )
    comment2 = Comment(
        id=uuid.uuid4(),
        task_id=task_id,
        user_id=auth_user.id,
        body="Second comment",
        created_at=datetime(2026, 7, 25, 11, 0, 0, tzinfo=timezone.utc)
    )
    comments_list = [comment1, comment2]
    
    def mock_execute(query):
        query_str = str(query)
        mock_res = MagicMock()
        if "FROM users" in query_str or "users.id" in query_str:
            mock_res.scalar_one_or_none.return_value = auth_user
            mock_res.scalar_one.return_value = auth_user
        elif "FROM tasks" in query_str or "tasks.id" in query_str:
            mock_res.scalar_one_or_none.return_value = task
            mock_res.scalar_one.return_value = task
        elif "FROM comments" in query_str or "comments.task_id" in query_str:
            mock_res.scalars.return_value.all.return_value = comments_list
        return mock_res
        
    db.execute.side_effect = mock_execute
    
    response = await client.get(f"/tasks/{task_id}/comments", headers=auth_headers)
    
    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp) == 2
    assert json_resp[0]["body"] == "First comment"
    assert json_resp[1]["body"] == "Second comment"


async def test_update_own_comment(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """
    author can update body,
    updated_at must be non-null after edit
    """
    task_id = uuid.uuid4()
    comment_id = uuid.uuid4()
    comment = Comment(
        id=comment_id,
        task_id=task_id,
        user_id=auth_user.id,
        body="Initial comment body",
        created_at=datetime.now(timezone.utc),
        updated_at=None
    )
    
    def mock_execute(query):
        query_str = str(query)
        mock_res = MagicMock()
        if "FROM users" in query_str or "users.id" in query_str:
            mock_res.scalar_one_or_none.return_value = auth_user
            mock_res.scalar_one.return_value = auth_user
        elif "FROM comments" in query_str or "comments.id" in query_str:
            mock_res.scalar_one_or_none.return_value = comment
            mock_res.scalar_one.return_value = comment
        return mock_res
        
    db.execute.side_effect = mock_execute
    
    def mock_refresh(obj):
        pass
    db.refresh.side_effect = mock_refresh
    
    payload = {"body": "Updated comment body"}
    
    response = await client.patch(f"/tasks/{task_id}/comments/{comment_id}", json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["body"] == "Updated comment body"
    assert json_resp["updated_at"] is not None
    db.commit.assert_called_once()


async def test_delete_comment_forbidden(client: httpx.AsyncClient, db: AsyncMock, auth_user: User, auth_headers: dict):
    """
    a second user cannot delete
    another user's comment, expects HTTP 403
    """
    task_id = uuid.uuid4()
    comment_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    comment = Comment(
        id=comment_id,
        task_id=task_id,
        user_id=other_user_id,
        body="Another user's comment content",
        created_at=datetime.now(timezone.utc),
        updated_at=None
    )
    
    def mock_execute(query):
        query_str = str(query)
        mock_res = MagicMock()
        if "FROM users" in query_str or "users.id" in query_str:
            mock_res.scalar_one_or_none.return_value = auth_user
            mock_res.scalar_one.return_value = auth_user
        elif "FROM comments" in query_str or "comments.id" in query_str:
            mock_res.scalar_one_or_none.return_value = comment
            mock_res.scalar_one.return_value = comment
        return mock_res
        
    db.execute.side_effect = mock_execute
    
    response = await client.delete(f"/tasks/{task_id}/comments/{comment_id}", headers=auth_headers)
    
    assert response.status_code == 403
    db.delete.assert_not_called()
