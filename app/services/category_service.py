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
from app.crud.category import category as crud_category
from fastapi import status, status
from app.core.exceptions import TaskNotFoundError, TaskForbiddenError, CategoryNotFoundError, CategoryForbiddenError, CommentNotFoundError, CommentForbiddenError, InvalidCredentialsError, DuplicateEmailError

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_categories(
    db: AsyncSession,
    user_id: uuid.UUID
) -> List[Category]:
    """
    ⚙️ Retrieve all categories owned by a specific user.

    🔒 Authorization Check: Filters strictly by `user_id` so users cannot view
    other users' categories.

    Args:
        db: The active database session.
        user_id: The UUID of the requesting user.

    Returns:
        List[Category]: A list of category records ordered alphabetically.
    """
    return await crud_category.get_by_owner(db, owner_id=user_id)


async def create_category(
    db: AsyncSession,
    user_id: uuid.UUID,
    category_in: CategoryCreate
) -> Category:
    """
    ⚙️ Create a new category for a user.

    🔒 Authorization Check: Associates the category directly with the requesting
    `user_id` to enforce ownership.

    Args:
        db: The active database session.
        user_id: The UUID of the user creating the category.
        category_in: The CategoryCreate schema containing category details.

    Returns:
        Category: The newly created category record.
    """
    db_category = await crud_category.create(
        db, 
        obj_in={"name": category_in.name, "user_id": user_id}
    )
    return db_category


async def get_category_by_id(
    db: AsyncSession,
    category_id: uuid.UUID,
    user_id: uuid.UUID
) -> Optional[Category]:
    """
    ⚙️ Fetch a single category by ID.

    🔒 Authorization Check: Compares category's owner `user_id` to the requesting
    `user_id`. Raises HTTP 403 Forbidden if ownership mismatch occurs.

    Args:
        db: The active database session.
        category_id: The UUID of the category to fetch.
        user_id: The UUID of the requesting user.

    Returns:
        Category: The category record, or None if not found.
    """
    db_category = await crud_category.get(db, id=category_id)

    if not db_category:
        return None

    # 🔒 Ownership Check: Verify category belongs to requesting user ID
    if db_category.user_id != user_id:
        raise CategoryForbiddenError()

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

    Args:
        db: The active database session.
        category_id: The UUID of the category to update.
        user_id: The UUID of the requesting user.
        category_in: The CategoryUpdate schema containing the new name.

    Returns:
        Category: The updated category record, or None if not found.
    """
    db_category = await get_category_by_id(db, category_id, user_id)
    if not db_category:
        return None

    db_category = await crud_category.update(
        db, db_obj=db_category, obj_in={"name": category_in.name}
    )
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

    Args:
        db: The active database session.
        category_id: The UUID of the category to delete.
        user_id: The UUID of the requesting user.

    Returns:
        bool: True if deleted successfully, False if not found.
    """
    db_category = await get_category_by_id(db, category_id, user_id)
    if not db_category:
        return False

    await crud_category.remove(db, id=category_id)
    return True
