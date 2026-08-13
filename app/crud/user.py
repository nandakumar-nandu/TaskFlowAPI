"""CRUD operations for User model."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from .base import CRUDBase

class CRUDUser(CRUDBase[User]):
    """User-specific CRUD operations with custom query methods."""

    async def get_by_email(
        self, db: AsyncSession, *, email: str
    ) -> Optional[User]:
        """Get a user by email address."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_active_users(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get all active users (soft-delete filter if applicable)."""
        result = await db.execute(
            select(User).where(User.is_active == True).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

# Instantiate for use in services
user = CRUDUser(User)
