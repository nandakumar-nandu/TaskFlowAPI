# -*- coding: utf-8 -*-
"""
💾 CATEGORY DATABASE MODEL (category.py)
--------------------------------------------
Defines the SQLAlchemy ORM model for the `categories` database table.

Categories are user-scoped classification buckets for tasks. A user can
create multiple categories (e.g. "Work", "Personal", "Urgent") and assign
their tasks to them. Each category belongs to exactly one user — different
users may have categories with the same name without conflict.

Deleting a category does NOT delete its associated tasks. Instead, PostgreSQL
sets those tasks' `category_id` column to NULL (`ondelete="SET NULL"`),
preserving the tasks while removing the classification link.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    """
    💾 Category Database Entity — maps to the `categories` table.

    Represents a user-owned classification label for tasks.

    Relationship:
      - tasks (one-to-many): All Task records classified under this category.
        Uses `passive_deletes="all"` which instructs SQLAlchemy NOT to issue
        individual UPDATE statements to set task.category_id = NULL on delete.
        Instead, it trusts PostgreSQL's own `ondelete="SET NULL"` constraint
        defined on the task.category_id foreign key, which is faster and atomic.
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
