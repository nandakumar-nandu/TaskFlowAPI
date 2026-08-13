import uuid
"""CRUD operations for Tag model."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tag import Tag
from .base import CRUDBase

class CRUDTag(CRUDBase[Tag]):
    """Tag-specific CRUD operations."""

    async def get_by_name_and_user(
        self, db: AsyncSession, *, name: str, user_id: uuid.UUID
    ) -> Optional[Tag]:
        """Get a tag by its name and owner."""
        result = await db.execute(
            select(Tag).where(Tag.name == name, Tag.user_id == user_id)
        )
        return result.scalar_one_or_none()

tag = CRUDTag(Tag)
