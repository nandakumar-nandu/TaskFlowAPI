# -*- coding: utf-8 -*-
"""
📝 COMMENT PYDANTIC SCHEMAS (comment.py)
--------------------------------------
Defines request validation and response schemas for task comments.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    # 📝 Data structure used for posting a comment
    body: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Text content of the comment (required, 1-2000 characters).",
        examples=["This is a helpful task comment."]
    )


class CommentUpdate(BaseModel):
    # 📝 Data structure used for full replacement of a comment body
    body: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Updated text content of the comment.",
        examples=["This is an updated task comment."]
    )


class CommentRead(BaseModel):
    # 📝 Response payload structure representing a comment
    id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) assigned to the comment."
    )
    task_id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) of the associated task."
    )
    user_id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) of the comment's author."
    )
    body: str = Field(
        ...,
        description="Raw comment text content."
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the comment was created."
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the comment was last updated (null if never edited)."
    )

    # ⚙️ Enable Pydantic v2 ORM mapping compatibility
    model_config = {
        "from_attributes": True
    }
