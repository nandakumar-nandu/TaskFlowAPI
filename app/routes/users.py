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

    Unlike /auth/me, this route exists under the /users domain to group profile
    management logically, though it performs the same function via get_current_user.

    Returns:
        UserRead: The authenticated user's profile metadata.
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

    Only the fields provided in the JSON payload are updated. All other fields
    remain unchanged.

    Returns:
        UserRead: The updated user's profile metadata.
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

    Uploads a new avatar image for the user.

    The file is stored physically on disk in the `media/avatars` directory, and
    the user's `avatar_url` database field is updated with the file path.
    Files exceeding 5 MB are rejected by the UploadSizeLimitMiddleware.

    Accepted MIME types: image/jpeg, image/png, image/webp.

    Raises:
        HTTPException (415): If the file format is unsupported.

    Returns:
        UserRead: The user's updated profile containing the new avatar_url.
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
