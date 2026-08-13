# -*- coding: utf-8 -*-
"""
📝 TAG PYDANTIC SCHEMAS (tag.py)
--------------------------------
Defines request validation and response schemas for tag metadata.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """
    📝 Shared base schema for tag input payloads.

    Tags are identified purely by name within a user's scope. The same name
    (e.g. 'work') can exist for different users simultaneously without conflict,
    enforced by the UniqueConstraint(name, user_id) in the Tag model.
    """
    # 📝 Standard tag fields shared across schemas
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the tag (required)."
    )


class TagCreate(TagBase):
    """
    📝 Schema for explicit tag creation.

    In practice, tags are created implicitly via the `tags` field in TaskCreate
    and TaskUpdate. The _resolve_tags helper in task_service.py handles the
    create-or-reuse logic automatically.
    """
    # 📝 Data required during tag creation
    pass


class TagRead(TagBase):
    """
    📝 Response schema for tags embedded inside TaskRead responses.

    Tags are never returned standalone — they always appear inside the `tags`
    array of a TaskRead object. `from_attributes=True` enables ORM mapping.
    """
    # 📝 Data structure returned in response bodies for tag details
    id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) assigned to the tag."
    )
    user_id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) of the user who owns this tag."
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the tag record was created."
    )

    # ⚙️ Enable Pydantic v2 ORM mapping compatibility
    model_config = {
        "from_attributes": True
    }
