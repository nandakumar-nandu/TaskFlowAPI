# -*- coding: utf-8 -*-
"""
💾 TASK DATABASE MODEL (task.py)
--------------------------------
Defines the SQLAlchemy database ORM model for tasks.
"""

import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Uuid, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

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

    # 📌 Current execution status of the task (Enum, defaults to todo)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False),
        default=TaskStatus.TODO,
        nullable=False,
        comment="Current execution status (todo, in_progress, done)"
    )

    # 📌 Priority importance level of the task (Enum, defaults to medium)
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, native_enum=False),
        default=TaskPriority.MEDIUM,
        nullable=False,
        comment="Priority level of the task (low, medium, high)"
    )

    # 📌 Specific deadline date for the task (Optional, timezone-aware)
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Deadline timestamp for the task"
    )

    # 📌 Foreign Key mapping the task to its creator user (Cascade on Delete)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key pointing to the user who owns this task"
    )

    # 📌 Timestamp when the task record was created (UTC timezone-aware)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when the task record was created"
    )
