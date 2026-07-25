# -*- coding: utf-8 -*-
"""
🛣️ TASK COMMENTS ROUTES (comments.py)
-------------------------------------
Implements nested route endpoints for task comments. All routes are protected by JWT.
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentRead
from app.services import comment_service

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["Comments"])


@router.get("", response_model=List[CommentRead])
async def get_comments_list(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ GET /tasks/{task_id}/comments
    Retrieves all comments associated with the specified task.
    Requires user ownership of the parent task.
    """
    return await comment_service.list_comments(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_new_comment(
    task_id: uuid.UUID,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ POST /tasks/{task_id}/comments
    Adds a new comment to the specified task.
    Requires user ownership of the parent task.
    """
    return await comment_service.create_comment(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
        payload=payload
    )


@router.patch("/{comment_id}", response_model=CommentRead)
async def update_existing_comment(
    task_id: uuid.UUID,
    comment_id: uuid.UUID,
    payload: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ PATCH /tasks/{task_id}/comments/{comment_id}
    Updates the body text of a comment.
    Enforces author ownership check.
    """
    return await comment_service.update_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id,
        payload=payload
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_comment(
    task_id: uuid.UUID,
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ DELETE /tasks/{task_id}/comments/{comment_id}
    Deletes a specific comment.
    Enforces author ownership check.
    """
    await comment_service.delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
