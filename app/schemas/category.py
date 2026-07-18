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
    # 📝 Standard category fields shared across schemas
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the category (required)."
    )


class CategoryCreate(CategoryBase):
    # 📝 Data required during category creation
    pass


class CategoryUpdate(CategoryBase):
    # 📝 Data required to update category
    pass


class CategoryRead(CategoryBase):
    # 📝 Data structure returned in response bodies for category details
    id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) assigned to the category."
    )
    user_id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) of the user who owns this category."
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the category record was created."
    )

    # ⚙️ Enable Pydantic v2 ORM mapping compatibility
    model_config = {
        "from_attributes": True
    }
