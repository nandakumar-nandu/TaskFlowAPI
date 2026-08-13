import uuid
"""CRUD operations for TaskActivity model."""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.activity import TaskActivity
from .base import CRUDBase

class CRUDActivity(CRUDBase[TaskActivity]):
    """Activity log CRUD operations."""

    async def get_by_task(
        self, db: AsyncSession, *, task_id: uuid.UUID, limit: int = 200
    ) -> List[TaskActivity]:
        """Get activity log for a task, newest first."""
        result = await db.execute(
            select(TaskActivity)
            .where(TaskActivity.task_id == task_id)
            .order_by(desc(TaskActivity.occurred_at))
            .limit(limit)
        )
        return list(result.scalars().all())

activity = CRUDActivity(TaskActivity)
