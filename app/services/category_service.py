# -*- coding: utf-8 -*-
"""
⚙️ CATEGORY BUSINESS LOGIC SERVICES (category_service.py)
-------------------------------------------------------
Implements transactional logic for category operations. Ensures users can
only query, update, or delete categories that belong to their account (strict ownership checking).
"""

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_categories(
    db: AsyncSession,
    user_id: uuid.UUID
) -> List[Category]:
    """
    ⚙️ Retrieve all categories owned by a specific user.
    🔒 Authorization Check: Filters strictly by user_id so users cannot view other users' categories.
    """
    stmt = select(Category).where(Category.user_id == user_id).order_by(Category.name.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_category(
    db: AsyncSession,
    user_id: uuid.UUID,
    category_in: CategoryCreate
) -> Category:
    """
    ⚙️ Create a new category for a user.
    🔒 Authorization Check: Associates the category directly with the requesting user_id to enforce ownership.
    """
    db_category = Category(
        name=category_in.name,
        user_id=user_id
    )
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def get_category_by_id(
    db: AsyncSession,
    category_id: uuid.UUID,
    user_id: uuid.UUID
) -> Optional[Category]:
    """
    ⚙️ Fetch a single category by ID.
    🔒 Authorization Check: Compares category's owner user_id to the requesting user_id.
    Raises HTTP 403 Forbidden if ownership mismatch occurs.
    """
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    db_category = result.scalar_one_or_none()

    if not db_category:
        return None

    # 🔒 Ownership Check: Verify category belongs to requesting user ID
    if db_category.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this category"
        )

    return db_category


async def update_category(
    db: AsyncSession,
    category_id: uuid.UUID,
    user_id: uuid.UUID,
    category_in: CategoryUpdate
) -> Optional[Category]:
    """
    ⚙️ Update an existing category name.
    🔒 Authorization Check: Verifies ownership of category before making modifications.
    Raises HTTP 403 Forbidden on authorization check failures.
    """
    db_category = await get_category_by_id(db, category_id, user_id)
    if not db_category:
        return None

    db_category.name = category_in.name
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def delete_category(
    db: AsyncSession,
    category_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    """
    ⚙️ Delete a specific category.
    🔒 Authorization Check: Verifies ownership of category before deletion.
    Raises HTTP 403 Forbidden on authorization check failures.
    """
    db_category = await get_category_by_id(db, category_id, user_id)
    if not db_category:
        return False

    await db.delete(db_category)
    await db.commit()
    return True
