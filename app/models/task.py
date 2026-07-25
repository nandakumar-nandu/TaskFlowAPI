# -*- coding: utf-8 -*-
"""
💾 TASK DATABASE MODEL (task.py)
--------------------------------
Defines the SQLAlchemy database ORM model for tasks.
"""

import uuid
import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Uuid, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TaskStatus(str, enum.Enum):
    # 📌 Enumeration of possible task statuses
    TODO = "todo"                # Task has been planned but not started
    IN_PROGRESS = "in_progress"  # Task is currently active/being worked on
    DONE = "done"                # Task has been successfully completed


class TaskPriority(str, enum.Enum):
    # 📌 Enumeration of possible task priority levels
    LOW = "low"                  # Minor importance, low urgency
    MEDIUM = "medium"            # Normal importance, moderate urgency
    HIGH = "high"                # High importance, must be completed immediately


class Task(Base):
    """
    💾 Task Database Entity.
    Represents an individual task owned by a user.
    """
    __tablename__ = "tasks"

    # 📌 Unique identifier for the task (Primary Key)
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the task (UUID)"
    )

    # 📌 Short title/summary of the task (Required)
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Short title/summary of the task"
    )

    # 📌 Long description detailing task instructions (Optional)
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="Long description detailing task instructions"
    )

    # 📌 Current execution status of the task (Enum, defaults to todo, Indexed)
    # Index explanation: Improves search performance when filtering tasks by their current status.
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False),
        default=TaskStatus.TODO,
        nullable=False,
        index=True,
        comment="Current execution status (todo, in_progress, done)"
    )

    # 📌 Priority importance level of the task (Enum, defaults to medium, Indexed)
    # Index explanation: Improves query performance when filtering tasks by their priority level.
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, native_enum=False),
        default=TaskPriority.MEDIUM,
        nullable=False,
        index=True,
        comment="Priority level of the task (low, medium, high)"
    )

    # 📌 Specific deadline date for the task (Optional, timezone-aware, Indexed)
    # Index explanation: Optimizes order-by queries when sorting tasks by due dates and range searches.
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
        comment="Deadline timestamp for the task"
    )

    # 📌 Foreign Key mapping the task to its creator user (Cascade on Delete, Indexed)
    # Index explanation: Critical index to scope queries strictly to the authenticated user's records.
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key pointing to the user who owns this task"
    )

    # 📌 Foreign Key referencing the task's category (Optional, Nullable, SET NULL on delete, Indexed)
    # Index explanation: Speeds up join operations and filtering tasks by category.
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        index=True,
        comment="Foreign key pointing to the category associated with this task"
    )

    # 📌 Timestamp when the task record was created (UTC timezone-aware)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when the task record was created"
    )

    # 🔗 Relationships
    # Many-to-one relationship with Category
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="tasks"
    )

    # Many-to-many relationship with Tag. Eager loads tags via selectin load strategy
    # to avoid N+1 queries when lists of tasks are fetched.
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="task_tags",
        back_populates="tasks",
        lazy="selectin"
    )

    # One-to-many relationship with Comment. Cascade delete orphan comment objects.
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="task",
        cascade="all, delete-orphan"
    )

