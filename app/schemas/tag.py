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
    # 📝 Standard tag fields shared across schemas
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the tag (required)."
    )


class TagCreate(TagBase):
    # 📝 Data required during tag creation
    pass


class TagRead(TagBase):
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
