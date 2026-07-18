# -*- coding: utf-8 -*-
"""
💾 TAG DATABASE MODEL & ASSOCIATION (tag.py)
--------------------------------------------
Defines the SQLAlchemy database ORM model for tags and the intermediate
association table for the many-to-many relationship between tasks and tags.

Many-to-Many Relationship Pattern:
A task can have multiple tags, and a tag can be associated with multiple tasks.
This is implemented using a junction table 'task_tags', which contains foreign keys
to both 'tasks' and 'tags'. By using a composite primary key of (task_id, tag_id),
we guarantee uniqueness of the relationship (no duplicate tag connections on a single task)
and automatically generate optimal index coverage for queries joining on task_id first.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Uuid, String, DateTime, ForeignKey, Table, Column, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# 🗃️ Many-to-Many Junction Table for Tasks and Tags
# This table maps the relationships and handles cascades. When a task or tag is deleted,
# the corresponding entries in this table are deleted automatically.
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column(
        "task_id",
        Uuid,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Foreign key referencing the task"
    ),
    Column(
        "tag_id",
        Uuid,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Foreign key referencing the tag"
    )
)


class Tag(Base):
    """
    💾 Tag Database Entity.
    Represents a customizable label/tag that can be associated with multiple tasks.
    Owned by a specific user to ensure data segregation.
    """
    __tablename__ = "tags"

    # 📌 Unique identifier for the tag (Primary Key)
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the tag (UUID)"
    )

    # 📌 Name of the tag (Required, e.g. "Work", "Urgent")
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Name of the tag"
    )

    # 📌 Foreign Key mapping the tag to its owner (Cascade on Delete)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key pointing to the user who owns this tag"
    )

    # 📌 Timestamp when the tag was created (UTC timezone-aware)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when the tag record was created"
    )

    # 🔗 Relationships
    # Many-to-many relationship with tasks
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=task_tags,
        back_populates="tags"
    )

    # 📌 Class level constraints
    # Ensures a single user cannot create duplicate tags by name, while allowing
    # different users to have tags with the same name.
    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_tag_name_user_id"),
    )
