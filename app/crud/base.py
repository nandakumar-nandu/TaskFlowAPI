"""Base class for CRUD operations with common patterns."""
from typing import Generic, Type, TypeVar, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

ModelType = TypeVar("ModelType")

class CRUDBase(Generic[ModelType]):
    """Generic CRUD operations for a SQLAlchemy model.
    
    Subclasses should override methods for model-specific logic.
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, *, obj_in: dict
    ) -> ModelType:
        """Create a new record."""
        obj_in_db = self.model(**obj_in)
        db.add(obj_in_db)
        await db.commit()
        await db.refresh(obj_in_db)
        return obj_in_db

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: dict
    ) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType:
        """Delete a record by ID."""
        obj = await self.get(db, id=id)
        if obj:
            await db.execute(delete(self.model).where(self.model.id == id))
            await db.commit()
        return obj
