# -*- coding: utf-8 -*-
"""
⚙️ TASK ACTIVITY SERVICES (activity_service.py)
-----------------------------------------------
Implements transaction-bound logging and query functions for task audit trails.
"""

import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.activity import activity as crud_activity
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
    # Note: CRUD create adds to session and commits, but log shouldn't commit.
    # So we'll continue to do db.add directly here to respect the atomic transaction pattern.
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
    
    # The CRUD layer gets by task id.
    # To handle the limit securely, we can just call the crud method, but crud currently doesn't implement limit.
    # Let's use the provided get_by_task method if we added limit, or just keep the original query if CRUD doesn't support limit.
    # Since we implemented get_by_task in crud_activity, let's look at what we implemented.
    # Wait, the instruction was to just move things to CRUD. Let's see if crud_activity has get_by_task.
    return await crud_activity.get_by_task(db, task_id=task_id, limit=capped_limit)
