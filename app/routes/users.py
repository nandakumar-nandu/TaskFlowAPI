# -*- coding: utf-8 -*-
"""
🛣️ USER PROFILE MANAGEMENT ROUTES (users.py)
---------------------------------------------
Exposes profile retrieval, modification, and avatar image uploads.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def read_my_profile(current_user: User = Depends(get_current_user)):
    """
    🛣️ GET /users/me
    Retrieves profile data of the logged-in user.
    🔒 Authorization: uses get_current_user dependency directly (no extra database lookup needed).
    """
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ PATCH /users/me
    Applies partial profile updates.
    """
    return await user_service.update_user(
        db=db,
        user_id=current_user.id,
        payload=payload
    )


@router.post("/me/avatar", response_model=UserRead)
async def upload_my_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🛣️ POST /users/me/avatar
    Uploads a new avatar image.
    Accepted MIME types: image/jpeg, image/png, image/webp.
    """
    # 🧪 Validate MIME Type
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported media type. Only image/jpeg, image/png, and image/webp are accepted."
        )
        
    return await user_service.save_avatar(
        db=db,
        user=current_user,
        file=file
    )
