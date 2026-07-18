# -*- coding: utf-8 -*-
"""
📝 TASK PYDANTIC SCHEMAS (task.py)
--------------------------------
Defines request validation and response schemas for tasks management.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.task import TaskStatus, TaskPriority
from app.schemas.tag import TagRead


class TaskBase(BaseModel):
    # 📝 Standard task fields shared across schemas
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Short title or summary of the task (required).",
        examples=["Implement database"]
    )
    description: Optional[str] = Field(
        None,
        description="Optional detailed markdown or text description of the task.",
        examples=["Configure models and database migrations using Alembic."]
    )
    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description="Current execution status of the task.",
        examples=["todo"]
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Priority importance level of the task.",
        examples=["high"]
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Optional deadline timestamp (UTC timezone-aware).",
        examples=["2026-07-22T18:00:00Z"]
    )
    category_id: Optional[uuid.UUID] = Field(
        None,
        description="Optional unique identifier of the category.",
        examples=["8a0a88bf-97cc-44a3-ad6c-9411649b8054"]
    )


class TaskCreate(TaskBase):
    # 📝 Data required during task creation
    tags: Optional[List[str]] = Field(
        None,
        description="Optional array of tag names to associate with the task.",
        examples=[["work", "important"]]
    )


class TaskUpdate(BaseModel):
    # 📝 Data structure used for modifying tasks (all fields optional)
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Optional updated title of the task.",
        examples=["Implement production database"]
    )
    description: Optional[str] = Field(
        None,
        description="Optional updated detailed description of the task.",
        examples=["Configure Postgres migrations inside docker containers."]
    )
    status: Optional[TaskStatus] = Field(
        None,
        description="Optional updated execution status of the task.",
        examples=["in_progress"]
    )
    priority: Optional[TaskPriority] = Field(
        None,
        description="Optional updated priority level of the task.",
        examples=["medium"]
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Optional updated deadline timestamp.",
        examples=["2026-07-25T12:00:00Z"]
    )
    category_id: Optional[uuid.UUID] = Field(
        None,
        description="Optional updated category identifier.",
        examples=["8a0a88bf-97cc-44a3-ad6c-9411649b8054"]
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Optional updated list of tag names (replaces existing tags).",
        examples=[["work", "devops"]]
    )


class TaskRead(TaskBase):
    # 📝 Data structure returned in response bodies for task details
    id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) assigned to the task.",
        examples=["f5c901e9-8967-43cd-ad1c-82b3cf1fg4b1"]
    )
    user_id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) of the user who owns this task.",
        examples=["7b0a88bf-97cc-44a3-ad6c-9411649b8032"]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the task record was created.",
        examples=["2026-07-15T17:30:00Z"]
    )
    tags: List[TagRead] = Field(
        default_factory=list,
        description="List of tag records associated with this task."
    )

    # ⚙️ Enable Pydantic v2 ORM mapping compatibility
    model_config = {
        "from_attributes": True
    }


class TaskListResponse(BaseModel):
    # 📝 Paginated list response wrapper containing metadata
    tasks: List[TaskRead] = Field(
        ...,
        description="Array of task records matching filter criteria."
    )
    total_count: int = Field(
        ...,
        description="Total matching tasks records count in the database.",
        examples=[1]
    )
    limit: int = Field(
        ...,
        description="The pagination page record limit used in query.",
        examples=[10]
    )
    offset: int = Field(
        ...,
        description="The pagination offset (number of skipped records) used in query.",
        examples=[0]
    )
    pages: int = Field(
        ...,
        description="The total calculated pages based on total_count and limit.",
        examples=[1]
    )


