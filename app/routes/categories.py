# -*- coding: utf-8 -*-
"""
🛣️ CATEGORY MANAGEMENT ROUTES (categories.py)
--------------------------------------------
Implements full CRUD routes for Category resources. All routes are protected by JWT authentication.
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.core.exceptions import TaskNotFoundError, TaskForbiddenError, CategoryNotFoundError, CategoryForbiddenError, CommentNotFoundError, CommentForbiddenError, InvalidCredentialsError, DuplicateEmailError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryRead])
async def read_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ GET /categories

    Retrieve a flat list of all categories created by the authenticated user.

    Returns:
        List[CategoryRead]: A list of category objects.
    """
    return await category_service.get_categories(db=db, user_id=current_user.id)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_new_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ POST /categories

    Create a new category bucket for the authenticated user.

    Returns:
        CategoryRead: The newly created category.
    """
    return await category_service.create_category(
        db=db,
        user_id=current_user.id,
        category_in=category_in
    )


@router.get("/{category_id}", response_model=CategoryRead)
async def read_category_by_id(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ GET /categories/{category_id}

    Retrieve details of a specific category by its UUID.

    Raises:
        HTTPException (404): If the category does not exist (or doesn't belong to the user).

    Returns:
        CategoryRead: The category details.
    """
    db_category = await category_service.get_category_by_id(
        db=db,
        category_id=category_id,
        user_id=current_user.id
    )
    if not db_category:
        raise CategoryNotFoundError()
    return db_category


@router.put("/{category_id}", response_model=CategoryRead)
async def update_existing_category(
    category_id: uuid.UUID,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ PUT /categories/{category_id}

    Rename an existing category.

    Raises:
        HTTPException (404): If the category does not exist (or doesn't belong to the user).

    Returns:
        CategoryRead: The updated category details.
    """
    db_category = await category_service.update_category(
        db=db,
        category_id=category_id,
        user_id=current_user.id,
        category_in=category_in
    )
    if not db_category:
        raise CategoryNotFoundError()
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ DELETE /categories/{category_id}

    Delete a category.

    Deleting a category does not delete its assigned tasks. Instead, any tasks
    using this category will have their `category_id` set to NULL automatically
    by PostgreSQL cascade rules.

    Raises:
        HTTPException (404): If the category does not exist (or doesn't belong to the user).

    Returns:
        HTTP 204 No Content on successful deletion.
    """
    success = await category_service.delete_category(
        db=db,
        category_id=category_id,
        user_id=current_user.id
    )
    if not success:
        raise CategoryNotFoundError()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
