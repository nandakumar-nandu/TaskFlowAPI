"""CRUD operations for Category model."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.category import Category
from .base import CRUDBase

class CRUDCategory(CRUDBase[Category]):
    """Category-specific CRUD operations."""

    async def get_by_owner(
        self, db: AsyncSession, *, owner_id: int
    ) -> List[Category]:
        """Get all categories owned by a user."""
        result = await db.execute(
            select(Category).where(Category.owner_id == owner_id)
        )
        return list(result.scalars().all())

category = CRUDCategory(Category)
