# -*- coding: utf-8 -*-
"""
⚙️ USER BUSINESS LOGIC SERVICES (user_service.py)
------------------------------------------------
Manages updates to user profile data and avatar file uploads.
"""

import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user as crud_user
from app.models.user import User
from app.schemas.user import UserUpdate


async def update_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    payload: UserUpdate
) -> User:
    """Applies partial updates to the user profile fields. Hashes the password if provided."""
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise ValueError("User not found")

    update_data = payload.model_dump(exclude_unset=True)
    
    # If password is provided, hash it before saving
    if "password" in update_data and update_data["password"]:
        from app.core.security import hash_password
        user.hashed_password = hash_password(update_data["password"])
        del update_data["password"]

    updated_user = await crud_user.update(db, db_obj=user, obj_in=update_data)
    return updated_user


async def save_avatar(
    db: AsyncSession,
    user: User,
    file: UploadFile
) -> User:
    """Saves the uploaded avatar image file to disk. Builds a deterministic filename using the user's UUID."""
    # Derive extension from content type
    mime_to_ext = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp"
    }
    ext = mime_to_ext.get(file.content_type or "", ".png")
    
    filename = f"{user.id}{ext}"
    
    # Target directory path
    media_dir = Path("media/avatars")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = media_dir / filename
    
    # Save/stream file using copyfileobj
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Store relative URL (e.g. "/media/avatars/uuid.png")
    relative_url = f"/media/avatars/{filename}"
    updated_user = await crud_user.update(db, db_obj=user, obj_in={"avatar_url": relative_url})
    return updated_user
