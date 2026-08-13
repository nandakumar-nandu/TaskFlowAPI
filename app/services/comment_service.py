# -*- coding: utf-8 -*-
"""
⚙️ COMMENT BUSINESS LOGIC SERVICES (comment_service.py)
------------------------------------------------------
Implements transactional logic for task comments with strict ownership check rules.
"""

import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.task import Task
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


async def _assert_task_owner(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID
) -> Task:
    """
    Private guard function to verify task existence and ownership.
    Returns 404 before 403 to prevent malicious actors from enumerating task UUIDs.
    """
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
        
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )
        
    return task


async def list_comments(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID
) -> List[Comment]:
    """List all comments on a given task. Caller must own the parent task to list its comments."""
    await _assert_task_owner(db, task_id, user_id)
    
    stmt = select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_comment(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: CommentCreate
) -> Comment:
    """Create a new comment on a task. Caller must own the parent task to comment on it."""
    await _assert_task_owner(db, task_id, user_id)
    
    db_comment = Comment(
        task_id=task_id,
        user_id=user_id,
        body=payload.body
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


async def update_comment(
    db: AsyncSession,
    comment_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: CommentUpdate
) -> Comment:
    """Update the body of a comment. Only the author of the comment can edit it."""
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
        
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this comment"
        )
        
    comment.body = payload.body
    comment.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(
    db: AsyncSession,
    comment_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    """Delete a specific comment. Only the author user can delete their comment."""
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
        
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment"
        )
        
    await db.delete(comment)
    await db.commit()
    return True
