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
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserUpdate


async def update_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    payload: UserUpdate
) -> User:
    """
    ⚙️ Applies partial updates to the user profile fields.
    Uses model_dump(exclude_unset=True) to avoid overwriting unsubmitted fields.
    """
    # Fetch User
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()

    # Apply updates
    update_data = payload.model_dump(exclude_unset=True)
    
    # If password is provided, hash it before saving
    if "password" in update_data and update_data["password"]:
        from app.core.security import hash_password
        user.hashed_password = hash_password(update_data["password"])
        del update_data["password"]

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


async def save_avatar(
    db: AsyncSession,
    user: User,
    file: UploadFile
) -> User:
    """
    ⚙️ Saves the uploaded avatar image file to disk.
    Builds a deterministic filename using the user's UUID to prevent file orphans.
    """
    # Derive extension from content type
    mime_to_ext = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp"
    }
    ext = mime_to_ext.get(file.content_type, ".png")
    
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
    user.avatar_url = relative_url
    
    await db.commit()
    await db.refresh(user)
    return user
