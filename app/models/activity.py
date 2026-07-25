# -*- coding: utf-8 -*-
"""
💾 TASK ACTIVITY DATABASE MODEL (activity.py)
---------------------------------------------
Defines the SQLAlchemy database ORM model for task mutation audit logs.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Uuid, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TaskActivity(Base):
    """
    💾 TaskActivity Database Entity.
    Append-only audit trail for task mutations.
    
    📌 Note on immutability:
    This table is append-only. No update or delete routes are ever exposed
    for activity rows.
    """
    __tablename__ = "task_activity"

    # 📌 Immutable primary key for this audit record
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Immutable primary key for this audit record"
    )

    # 📌 Foreign key pointing to the task (Cascade on delete, Indexed)
    # Index explanation: Activity records are always queried by task_id
    task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key pointing to the task being audited"
    )

    # 📌 Foreign key pointing to the user who performed the mutation (SET NULL on delete)
    # SET NULL explanation: Preserves audit trail history even if user account is deleted
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        comment="Foreign key pointing to the acting user (nullable if user deleted)"
    )

    # 📌 Event action type label (task.created, task.updated, task.deleted)
    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Event type label (task.created, task.updated, task.deleted)"
    )

    # 📌 JSON snapshot of changed fields: {"field": {"before": old_val, "after": new_val}}
    diff: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        default=None,
        comment="JSON snapshot of changed fields (null for create and delete events)"
    )

    # 📌 UTC timestamp when the event was recorded
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="UTC timestamp when the audit event was recorded"
    )
