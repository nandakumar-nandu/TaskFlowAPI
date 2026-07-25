# -*- coding: utf-8 -*-
"""
💾 COMMENT DATABASE MODEL (comment.py)
--------------------------------------
Defines the SQLAlchemy database ORM model for task comments.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Uuid, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Comment(Base):
    """
    💾 Comment Database Entity.
    Represents an individual comment posted by a user on a task.
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
