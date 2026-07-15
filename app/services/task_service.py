# -*- coding: utf-8 -*-
"""
⚙️ TASK BUSINESS LOGIC SERVICES (task_service.py)
-----------------------------------------------
Implements transactional logic for task operations. Ensures users can
only query, update, or delete tasks that belong to their account (strict ownership checking).
"""

import uuid
import math
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate


async def get_tasks(
    db: AsyncSession,
    user_id: uuid.UUID,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    skip: int = 0,
    limit: int = 10
) -> Dict[str, Any]:
    """
    ⚙️ Retrieve a paginated list of tasks owned by a specific user.
    🔒 Authorization Check: Filters queries strictly by user_id so users cannot view tasks of other accounts.
    """
    # ⚙️ Build dynamic query clauses
    query = select(Task).where(Task.user_id == user_id)
    count_query = select(func.count(Task.id)).where(Task.user_id == user_id)
    
    if status:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)
        
    if priority:
        query = query.where(Task.priority == priority)
        count_query = count_query.where(Task.priority == priority)
        
    # ⚙️ Order tasks by creation time descending
    query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    
    # ⚙️ Execute database count and fetch operations asynchronously
    count_result = await db.execute(count_query)
    total_count = count_result.scalar() or 0
    
    tasks_result = await db.execute(query)
    tasks = list(tasks_result.scalars().all())
    
    # ⚙️ Calculate page numbers
    pages = math.ceil(total_count / limit) if limit > 0 else 0
    
    return {
        "tasks": tasks,
        "total_count": total_count,
        "limit": limit,
        "offset": skip,
        "pages": pages
    }


async def create_task(
    db: AsyncSession,
    user_id: uuid.UUID,
    task_in: TaskCreate
) -> Task:
    """
    ⚙️ Register a new task.
    🔒 Authorization Check: Associates the task directly with the creator user_id to enforce ownership.
    """
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        user_id=user_id
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    task_in: TaskUpdate
) -> Optional[Task]:
    """
    ⚙️ Modify details of a specific task.
    🔒 Authorization Check: Fetches task by task_id first and compares the owned user_id.
    Raises HTTP 403 Forbidden if the task belongs to another user.
    """
    # ⚙️ Fetch task instance and verify ownership
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        return None
        
    # 🔒 Ownership Check: Verify task belongs to requesting user ID
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task"
        )
        
    # ⚙️ Apply fields changes
    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def delete_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    """
    ⚙️ Delete a specific task.
    🔒 Authorization Check: Fetches task by task_id first and checks ownership.
    Raises HTTP 403 Forbidden if the task belongs to another user.
    """
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        return False
        
    # 🔒 Ownership Check: Verify task belongs to requesting user ID
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task"
        )
        
    await db.delete(db_task)
    await db.commit()
    return True
