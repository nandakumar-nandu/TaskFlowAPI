# -*- coding: utf-8 -*-
"""
💾 USER DATABASE MODEL (user.py)
--------------------------------
Defines the SQLAlchemy ORM model for the `users` database table.

The User entity is the root owner of all other resources in the system.
Every Task, Category, Tag, and Comment has a user_id foreign key pointing
back to this table. When a User is deleted, PostgreSQL's cascade rules
automatically delete all their owned records (tasks, categories, tags, comments).

This model intentionally does NOT declare ORM relationship fields (e.g.
user.tasks). Ownership is instead enforced at the service layer by filtering
all queries with `WHERE user_id = <current_user.id>`, which is cleaner and
avoiders N+1 query risks on large datasets.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Uuid, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """
    💾 User Database Entity — maps to the `users` table.

    Represents a registered user account. Stores authentication credentials
    (hashed password, not plain text), profile metadata, account status, and
    an optional avatar image URL.

    Ownership pattern: Every other table (tasks, categories, tags, comments,
    task_activity) has a user_id FK that references this table's `id` column.
    Cascades ensure full cleanup on account deletion.
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
    # 📌 URL to the user's uploaded avatar image (Optional)
    avatar_url: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        default=None,
        comment="stores relative URL to uploaded avatar image"
    )
    # 📌 Timestamp when the user registered (UTC timezone-aware)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when the user account was created"
    )
