# -*- coding: utf-8 -*-
"""
💾 TASK ACTIVITY DATABASE MODEL (activity.py)
------------------------------------------------------
Defines the SQLAlchemy ORM model for the `task_activity` table.

This table implements an append-only audit trail for task mutations.
Every time a task is created, updated, or deleted, one row is inserted here
to record what happened, who did it, and (for updates) what changed.

Key design decisions:
  - APPEND-ONLY: No UPDATE or DELETE routes are ever exposed for these rows.
    Once written, an activity record is permanent, providing a trustworthy audit log.
  - NULLABLE user_id: The user_id FK uses SET NULL on delete. This preserves
    audit history even after the acting user's account is deleted — the event
    remains in the log but user_id becomes null.
  - diff JSON: For task.updated events, the diff column stores a JSON object
    mapping changed field names to {"before": old_value, "after": new_value} pairs.
    For task.created and task.deleted events, diff is null (no field comparison needed).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Uuid, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TaskActivity(Base):
    """
    💾 TaskActivity Database Entity — maps to the `task_activity` table.

    Append-only audit trail for task lifecycle events.

    Lifecycle events recorded:
      - `task.created` : diff is null (no before/after, the task is new)
      - `task.updated` : diff contains only the fields that changed
      - `task.deleted` : diff is null (the task row will be cascade-deleted)

    Immutability guarantee:
      This model has NO UPDATE or DELETE service methods. The service layer
      (activity_service.log) only adds rows — it never modifies existing ones.
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
