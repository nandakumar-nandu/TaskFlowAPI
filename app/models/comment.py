# -*- coding: utf-8 -*-
"""
💾 COMMENT DATABASE MODEL (comment.py)
-----------------------------------------------
Defines the SQLAlchemy ORM model for the `comments` database table.

A Comment is a text annotation posted by a user on a specific task.
It links two entities: the parent Task (task_id FK) and the authoring
User (user_id FK). Both foreign keys cascade-delete — if either the
parent task or the author user is deleted, all their comments are also
automatically removed by the database.

Edit and delete permissions are authorship-based (not task-ownership-based):
only the user who wrote a comment (user_id == current_user.id) is allowed
to modify or delete it, even if another user owns the parent task.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Uuid, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Comment(Base):
    """
    💾 Comment Database Entity — maps to the `comments` table.

    Represents a user-authored text annotation on a specific task.

    Relationships:
      - task (many-to-one): The parent task this comment belongs to.
      - author (many-to-one): The User who wrote this comment.
        Uses `lazy="joined"` (JOIN load strategy) so the author record is
        fetched in the same query as the comment, avoiding a separate round-trip.
    """
    __tablename__ = "comments"

    # 📌 Unique identifier for the comment (Primary Key)
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the comment (UUID)"
    )

    # 📌 Foreign Key referencing the parent task (Cascade on Delete, Indexed)
    task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key pointing to the task associated with this comment"
    )

    # 📌 Foreign Key referencing the author user (Cascade on Delete, Nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key pointing to the user who wrote this comment"
    )

    # 📌 Body content of the comment (Required)
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Raw comment text content"
    )

    # 📌 Timestamp when the comment was created (UTC timezone-aware)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when the comment was created"
    )

    # 📌 Timestamp when the comment was updated (UTC timezone-aware, Nullable)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp when the comment was last updated"
    )

    # 🔗 Relationships
    # Many-to-one relationship with Task
    task: Mapped["Task"] = relationship("Task", back_populates="comments")
    
    # Many-to-one relationship with User (author). Eager loads author via joined strategy.
    author: Mapped["User"] = relationship("User", lazy="joined")
