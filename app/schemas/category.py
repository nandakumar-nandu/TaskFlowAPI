# -*- coding: utf-8 -*-
"""
📝 CATEGORY PYDANTIC SCHEMAS (category.py)
----------------------------------------
Defines request validation and response schemas for category management.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """
    📝 Shared base schema for category input payloads.

    The `name` field has a min_length=1 constraint to prevent empty string
    category names from being accepted. Max 255 characters.
    """
    # 📝 Standard category fields shared across schemas
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the category (required).",
        examples=["Work Tasks"]
    )


class CategoryCreate(CategoryBase):
    """
    📝 Request schema for POST /categories.

    Inherits `name` from CategoryBase. No additional fields are required
    since user ownership is assigned automatically from the JWT token context.
    """
    # 📝 Data required during category creation
    pass


class CategoryUpdate(CategoryBase):
    """
    📝 Request schema for PUT /categories/{category_id}.

    Inherits `name` from CategoryBase. Only the name can be changed.
    """
    # 📝 Data required to update category
    pass


class CategoryRead(CategoryBase):
    """
    📝 Response schema for all category endpoints that return a category.

    Used as the `response_model` for:
      GET  /categories          → 200 OK (as list element)
      POST /categories          → 201 Created
      GET  /categories/{id}     → 200 OK
      PUT  /categories/{id}     → 200 OK
    """
    # 📝 Data structure returned in response bodies for category details
    id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) assigned to the category.",
        examples=["8a0a88bf-97cc-44a3-ad6c-9411649b8054"]
    )
    user_id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) of the user who owns this category.",
        examples=["7b0a88bf-97cc-44a3-ad6c-9411649b8032"]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the category record was created.",
        examples=["2026-07-15T17:23:00Z"]
    )

    # ⚙️ Enable Pydantic v2 ORM mapping compatibility
    model_config = {
        "from_attributes": True
    }

