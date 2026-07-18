# -*- coding: utf-8 -*-
"""
💾 CATEGORY DATABASE MODEL (category.py)
------------------------------------
Defines the SQLAlchemy database ORM model for task categories.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    """
    💾 Category Database Entity.
    Represents a classification category for tasks, owned by a specific user.
    """
    __tablename__ = "categories"

    # 📌 Unique identifier for the category (Primary Key)
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the category (UUID)"
    )

    # 📌 Name of the category (Required, e.g. "Work", "Personal")
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Name of the category"
    )

    # 📌 Foreign Key mapping the category to its owner (Cascade on Delete)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key pointing to the user who owns this category"
    )

    # 📌 Timestamp when the category was created (UTC timezone-aware)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when the category record was created"
    )

    # 🔗 Relationships
    # One-to-many relationship with tasks. Passive deletes prevent SQLAlchemy from setting foreign keys
    # to NULL manually when a category is deleted; PostgreSQL's ondelete rules handle it natively.
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="category",
        passive_deletes="all"
    )
