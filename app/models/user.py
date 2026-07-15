# -*- coding: utf-8 -*-
"""
💾 USER DATABASE MODEL (user.py)
--------------------------------
Defines the SQLAlchemy database ORM model for user accounts.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Uuid, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """
    💾 User Database Entity.
    Represents a registered user account in the system.
    """
    __tablename__ = "users"

    # 📌 Unique identifier for the user (Primary Key)
    # Generates a random UUIDv4 default value.
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the user (UUID)"
    )

    # 📌 User's email address (Unique constraint, Indexed for search queries)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique email address of the user"
    )

    # 📌 Securely hashed password string (Bcrypt hash)
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Securely hashed password string"
    )

    # 📌 Display name of the user (Optional)
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        comment="Full name of the user"
    )

    # 📌 Account active status flag
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indicates if the user account is active"
    )

    # 📌 Timestamp when the user registered (UTC timezone-aware)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when the user account was created"
    )
