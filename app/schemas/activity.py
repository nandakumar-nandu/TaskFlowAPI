# -*- coding: utf-8 -*-
"""
📝 TASK ACTIVITY SCHEMAS (activity.py)
--------------------------------------
Defines response serialization schemas for task audit log entries.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ActivityRead(BaseModel):
    """
    📝 Response schema for GET /tasks/{task_id}/activity.

    Represents a single immutable audit log entry in the task's activity trail.

    Fields:
      id          → Unique identifier of this log entry.
      task_id     → The task this entry audits.
      user_id     → The user who performed the action (null if the user was later deleted).
      action      → Event type string: 'task.created', 'task.updated', or 'task.deleted'.
      diff        → For 'task.updated' events: JSON map of changed fields as
                    {"field_name": {"before": old_value, "after": new_value}}.
                    Null for 'task.created' and 'task.deleted' events.
      occurred_at → UTC timestamp when this event was recorded.

    `from_attributes=True` enables ORM-to-Pydantic mapping from TaskActivity objects.
    """
    id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) assigned to the activity log entry."
    )
    task_id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) of the audited task."
    )
    # 📌 Note: user_id can be null if the user account was deleted after the audit event was logged
    user_id: Optional[uuid.UUID] = Field(
        None,
        description="Unique identifier (UUID) of the acting user (null if user deleted)."
    )
    action: str = Field(
        ...,
        description="Action type label (e.g., task.created, task.updated, task.deleted)."
    )
    diff: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON snapshot of changed fields (null for create and delete events)."
    )
    occurred_at: datetime = Field(
        ...,
        description="UTC timestamp when the audit event was recorded."
    )

    # ⚙️ Enable Pydantic v2 ORM mapping compatibility
    model_config = {
        "from_attributes": True
    }
