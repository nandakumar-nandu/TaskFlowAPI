# -*- coding: utf-8 -*-
"""
🛣️ TASK MANAGEMENT ROUTES (tasks.py)
------------------------------------
Implements full CRUD routes for Task resources. All routes are protected by JWT authentication.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskListResponse
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=TaskListResponse)
async def read_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ GET /tasks
    Retrieve a paginated list of tasks matching the optional status/priority filters.
    Protected by JWT.
    """
    return await task_service.get_tasks(
        db=db,
        user_id=current_user.id,
        status=status,
        priority=priority,
        skip=skip,
        limit=limit
    )


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ POST /tasks
    Create a new task for the authenticated user.
    Protected by JWT.
    """
    return await task_service.create_task(
        db=db,
        user_id=current_user.id,
        task_in=task_in
    )


@router.get("/{task_id}", response_model=TaskRead)
async def read_task_by_id(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ GET /tasks/{task_id}
    Retrieve details of a specific task by ID.
    Enforces ownership check.
    Protected by JWT.
    """
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
        
    # 🔒 Ownership Check: Verify requester owns the task
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )
        
    return db_task


@router.put("/{task_id}", response_model=TaskRead)
async def update_existing_task(
    task_id: uuid.UUID,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ PUT /tasks/{task_id}
    Update details of a specific task.
    Enforces ownership check.
    Protected by JWT.
    """
    db_task = await task_service.update_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
        task_in=task_in
    )
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ DELETE /tasks/{task_id}
    Delete a specific task.
    Enforces ownership check.
    Protected by JWT.
    """
    success = await task_service.delete_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
