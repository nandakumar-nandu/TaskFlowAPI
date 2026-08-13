import uuid
"""CRUD operations for Task model."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task
from .base import CRUDBase

class CRUDTask(CRUDBase[Task]):
    """Task-specific CRUD operations with custom query methods."""

    async def get_by_owner(
        self, db: AsyncSession, *, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """Get all tasks owned by a specific user."""
        result = await db.execute(
            select(Task).where(Task.user_id == owner_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """Get tasks filtered by status."""
        result = await db.execute(
            select(Task).where(Task.status == status).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

# Instantiate for use in services
task = CRUDTask(Task)
