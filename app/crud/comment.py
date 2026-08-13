import uuid
"""CRUD operations for Comment model."""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.comment import Comment
from .base import CRUDBase

class CRUDComment(CRUDBase[Comment]):
    """Comment-specific CRUD operations."""

    async def get_by_task(
        self, db: AsyncSession, *, task_id: uuid.UUID
    ) -> List[Comment]:
        """Get all comments for a specific task."""
        result = await db.execute(
            select(Comment).where(Comment.task_id == task_id)
        )
        return list(result.scalars().all())

comment = CRUDComment(Comment)
