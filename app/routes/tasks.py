# -*- coding: utf-8 -*-
"""
🛣️ TASK MANAGEMENT ROUTES (tasks.py)
------------------------------------
Implements full CRUD routes for Task resources. All routes are protected by JWT authentication.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskListResponse
from app.schemas.activity import ActivityRead
from app.services import task_service, activity_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=TaskListResponse)
async def read_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    category_id: Optional[uuid.UUID] = None,
    tag: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    sort: str = "created_at",
    order: str = "desc",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ GET /tasks

    Retrieve a paginated, sorted list of tasks owned by the authenticated user.

    Supports dynamic filtering via query parameters (status, priority, category_id, tag).
    Pagination is controlled via `page` and `limit`. Sorting is controlled via `sort` and `order`.

    Returns:
        TaskListResponse: A paginated envelope containing the list of tasks and pagination metadata.
    """
    return await task_service.get_tasks(
        db=db,
        user_id=current_user.id,
        status=status,
        priority=priority,
        category_id=category_id,
        tag=tag,
        page=page,
        limit=limit,
        sort=sort,
        order=order
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

    Optionally links the task to a Category (if category_id is provided).
    Optionally creates or reuses Tags (if a list of tag strings is provided).

    Returns:
        TaskRead: The fully populated task object including eagerly-loaded tags.
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

    Retrieve details of a specific task by its UUID.

    Enforces ownership: The requesting user must own the task.

    Raises:
        HTTPException (404): If the task does not exist.
        HTTPException (403): If the task belongs to a different user.

    Returns:
        TaskRead: The task details.
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

    Update an existing task.

    Only updates the fields explicitly provided in the payload. If the `tags` array
    is provided, it completely replaces the current tags for the task.

    Raises:
        HTTPException (404): If the task does not exist (or doesn't belong to the user).

    Returns:
        TaskRead: The updated task details.
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

    Permanently delete a specific task.

    Cascades to delete all comments associated with this task.

    Raises:
        HTTPException (404): If the task does not exist (or doesn't belong to the user).

    Returns:
        HTTP 204 No Content on successful deletion.
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


@router.get("/{task_id}/activity", response_model=list[ActivityRead])
async def read_task_activity(
    task_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ GET /tasks/{task_id}/activity

    Retrieves the append-only activity audit trail for a task.

    The audit trail records lifecycle events (created, updated, deleted) and includes
    a JSON diff of changed fields for update events.

    Raises:
        HTTPException (404): If the task does not exist.
        HTTPException (403): If the requesting user does not own the task.

    Returns:
        List[ActivityRead]: A list of activity records, ordered newest to oldest.
    """
    # 🔒 Ownership check: Verify task exists and belongs to the authenticated user
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
        
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task activity"
        )
        
    return await activity_service.get_activity(
        db=db,
        task_id=task_id,
        limit=limit
    )
