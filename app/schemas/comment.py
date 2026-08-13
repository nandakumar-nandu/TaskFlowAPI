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
    """
    📝 Request schema for POST /tasks/{task_id}/comments.

    The `body` field is required and validated to be between 1 and 2000 characters.
    Empty comment bodies are explicitly rejected by the min_length=1 constraint.
    """
    # 📝 Data structure used for posting a comment
    body: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Text content of the comment (required, 1-2000 characters).",
        examples=["This is a helpful task comment."]
    )


class CommentUpdate(BaseModel):
    """
    📝 Request schema for PATCH /tasks/{task_id}/comments/{comment_id}.

    Replaces the entire comment body. This is a full replacement (not partial),
    so the `body` field is required even though only the body can be updated.
    The service layer also stamps the `updated_at` timestamp on save.
    """
    # 📝 Data structure used for full replacement of a comment body
    body: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Updated text content of the comment.",
        examples=["This is an updated task comment."]
    )


class CommentRead(BaseModel):
    """
    📝 Response schema for all comment endpoints that return a comment.

    Used as the `response_model` for:
      GET  /tasks/{task_id}/comments              → 200 OK (as list element)
      POST /tasks/{task_id}/comments              → 201 Created
      PATCH /tasks/{task_id}/comments/{id}        → 200 OK

    `updated_at` is None until the comment has been edited at least once.
    """
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
