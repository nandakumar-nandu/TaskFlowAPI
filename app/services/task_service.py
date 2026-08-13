# -*- coding: utf-8 -*-
"""
⚙️ TASK BUSINESS LOGIC SERVICES (task_service.py)
-----------------------------------------------
Implements transactional logic for task operations. Ensures users can
only query, update, or delete tasks that belong to their account (strict ownership checking).
Supports categories verification, tags mapping, dynamic filtering, sorting, and pagination.
"""

import uuid
import math
import enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.category import Category
from app.models.tag import Tag
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import activity_service


async def get_tasks(
    db: AsyncSession,
    user_id: uuid.UUID,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    category_id: Optional[uuid.UUID] = None,
    tag: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    sort: str = "created_at",
    order: str = "desc"
) -> Dict[str, Any]:
    """Retrieve a paginated, filtered, and sorted list of tasks, strictly scoped to the requesting user_id."""
    query = select(Task).where(Task.user_id == user_id)
    count_query = select(func.count(Task.id)).where(Task.user_id == user_id)
    if status:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)
        
    if priority:
        query = query.where(Task.priority == priority)
        count_query = count_query.where(Task.priority == priority)

    if category_id:
        query = query.where(Task.category_id == category_id)
        count_query = count_query.where(Task.category_id == category_id)

    if tag:
        query = query.join(Task.tags).where(Tag.name == tag)
        count_query = count_query.join(Task.tags).where(Tag.name == tag)
        
    # White-list columns to prevent SQL injection or attribute access errors
    sort_fields = ["due_date", "created_at", "priority", "status", "title"]
    sort_column_name = sort if sort in sort_fields else "created_at"
    sort_column = getattr(Task, sort_column_name)

    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    page = max(1, page)
    limit = max(1, limit)
    skip = (page - 1) * limit

    query = query.offset(skip).limit(limit)
    
    count_result = await db.execute(count_query)
    total_count = count_result.scalar() or 0
    
    tasks_result = await db.execute(query)
    tasks = list(tasks_result.scalars().all())
    
    # Calculate page numbers
    pages = math.ceil(total_count / limit) if limit > 0 else 0
    
    return {
        "tasks": tasks,
        "total_count": total_count,
        "limit": limit,
        "offset": skip,
        "pages": pages
    }


async def _resolve_tags(
    db: AsyncSession,
    user_id: uuid.UUID,
    tag_names: List[str]
) -> List[Tag]:
    """Helper method to retrieve existing tag objects or create new ones, scoped to user_id to prevent duplication."""
    resolved_tags = []
    for tag_name in tag_names:
        tag_name_stripped = tag_name.strip()
        if not tag_name_stripped:
            continue
        
        if not db_tag:
            db_tag = Tag(name=tag_name_stripped, user_id=user_id)
            db.add(db_tag)
            
        resolved_tags.append(db_tag)
    return resolved_tags


async def create_task(
    db: AsyncSession,
    user_id: uuid.UUID,
    task_in: TaskCreate
) -> Task:
    """Create a new task and log the creation activity. Validates category ownership if provided."""
    if task_in.category_id:
        stmt = select(Category).where(Category.id == task_in.category_id, Category.user_id == user_id)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    # Resolve tags
    db_tags = []
    if task_in.tags:
        db_tags = await _resolve_tags(db, user_id, task_in.tags)

    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        category_id=task_in.category_id,
        user_id=user_id,
        tags=db_tags
    )
    db.add(db_task)
    await db.flush()
    # Log task creation within the same transaction before commit
    activity_service.log(db, db_task.id, user_id, "task.created")
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    task_in: TaskUpdate
) -> Optional[Task]:
    """Modify details of a specific task. Computes field diffs and logs the change to task_activity."""
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        return None
        
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task"
        )
        
    # 🔒 Category Ownership Validation (if updating category_id)
    if task_in.category_id is not None:
        stmt = select(Category).where(Category.id == task_in.category_id, Category.user_id == user_id)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    # Compute field diffs BEFORE applying changes to capture genuine before values
    update_data = task_in.model_dump(exclude_unset=True, exclude={"tags"})
    diff = {}
    for key, value in update_data.items():
        old_val = getattr(db_task, key)
        if old_val != value:
            old_str = old_val.value if isinstance(old_val, enum.Enum) else (str(old_val) if isinstance(old_val, (uuid.UUID, datetime)) else old_val)
            new_str = value.value if isinstance(value, enum.Enum) else (str(value) if isinstance(value, (uuid.UUID, datetime)) else value)
            diff[key] = {"before": old_str, "after": new_str}
            setattr(db_task, key, value)
            
    if task_in.tags is not None:
        db_tags = await _resolve_tags(db, user_id, task_in.tags)
        db_task.tags = db_tags

    if diff:
        activity_service.log(db, db_task.id, user_id, "task.updated", diff=diff)

    await db.commit()
    await db.refresh(db_task)
    return db_task


async def delete_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    """Delete a specific task and log the deletion event."""
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        return False
        
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task"
        )
        
    activity_service.log(db, db_task.id, user_id, "task.deleted")
    await db.delete(db_task)
    await db.commit()
    return True
