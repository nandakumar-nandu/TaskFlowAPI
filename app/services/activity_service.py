# -*- coding: utf-8 -*-
"""
⚙️ TASK ACTIVITY SERVICES (activity_service.py)
-----------------------------------------------
Implements transaction-bound logging and query functions for task audit trails.
"""

import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.activity import TaskActivity


def log(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: Optional[uuid.UUID],
    action: str,
    diff: Optional[Dict[str, Any]] = None
) -> TaskActivity:
    """
    ⚙️ Creates a TaskActivity instance and adds it to the current database session.
    
    🔒 Atomic Transaction Pattern:
    This function does NOT call `await db.commit()`. The caller (e.g. `task_service`)
    is responsible for committing. This keeps the log entry and the task mutation
    in the same atomic transaction — if the task mutation rolls back, the log entry
    rolls back too.

    Args:
        db: The active database session.
        task_id: The UUID of the affected task.
        user_id: The UUID of the acting user (can be None).
        action: The event string (e.g., 'task.created', 'task.updated').
        diff: A dictionary of changed fields (optional).

    Returns:
        TaskActivity: The unstored activity instance added to the session.
    """
    activity = TaskActivity(
        task_id=task_id,
        user_id=user_id,
        action=action,
        diff=diff
    )
    db.add(activity)
    return activity


async def get_activity(
    db: AsyncSession,
    task_id: uuid.UUID,
    limit: int = 50
) -> List[TaskActivity]:
    """
    ⚙️ Retrieves audit activity logs for a specific task.

    Results are ordered by `occurred_at` descending (newest first).
    
    🛡️ Hard cap protection:
    Applies a hard cap of min(limit, 200) to prevent runaway queries on
    tasks with exceptionally long histories.

    Args:
        db: The active database session.
        task_id: The UUID of the task to fetch logs for.
        limit: The maximum number of records to return.

    Returns:
        List[TaskActivity]: A list of activity records.
    """
    capped_limit = min(max(1, limit), 200)
    
    stmt = (
        select(TaskActivity)
        .where(TaskActivity.task_id == task_id)
        .order_by(TaskActivity.occurred_at.desc())
        .limit(capped_limit)
    )
    
    result = await db.execute(stmt)
    return list(result.scalars().all())
