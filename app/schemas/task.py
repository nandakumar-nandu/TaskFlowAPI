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
    """
    📝 Shared base schema for task input payloads.

    Defines the core task fields with their validation rules and defaults.
    Inherited by TaskCreate (for creation) and used as the field source for
    TaskRead (for response serialization).
    """
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
    """
    📝 Request schema for POST /tasks.

    Accepts all TaskBase fields plus an optional `tags` list.
    Tag names are resolved by the service layer: existing tags (matched by
    name + user_id) are reused; new tag names trigger tag creation automatically.
    """
    # 📝 Data required during task creation
    tags: Optional[List[str]] = Field(
        None,
        description="Optional array of tag names to associate with the task.",
        examples=[["work", "important"]]
    )


class TaskUpdate(BaseModel):
    """
    📝 Request schema for PUT /tasks/{task_id}.

    All fields are optional — only submitted fields are applied.
    If `tags` is provided (even as an empty list), it replaces ALL existing
    tag associations on the task. Omitting `tags` entirely leaves tags unchanged.
    """
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
    """
    📝 Response schema for all task-related endpoints that return a single task.

    Used as the `response_model` for:
      POST /tasks       → 201 Created
      GET  /tasks/{id}  → 200 OK
      PUT  /tasks/{id}  → 200 OK

    Tags are eagerly loaded by the ORM (lazy="selectin") so they are always
    present in the response without requiring an extra query.
    `from_attributes=True` enables ORM-to-schema mapping.
    """
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
    """
    📝 Response schema for GET /tasks.

    Wraps a paginated list of tasks with metadata about the total result set.
    Allows clients to implement pagination UI (e.g. "Page 2 of 5").

    Fields:
      tasks       → The current page of TaskRead objects
      total_count → Total matching tasks across ALL pages
      limit       → The page size used in the query
      offset      → Number of records skipped before this page
      pages       → Total pages = ceil(total_count / limit)
    """
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


