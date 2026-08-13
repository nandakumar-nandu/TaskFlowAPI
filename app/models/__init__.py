# -*- coding: utf-8 -*-
"""
💾 DATABASE MODELS PACKAGE (__init__.py)
-----------------------------------------
This file makes the `app/models/` directory a Python package and exports
every ORM model class for convenient import elsewhere.

Why are all models imported here?
  SQLAlchemy's Alembic migration tool discovers tables by scanning the
  `Base.metadata` registry (defined in app/core/database.py). For a table
  to appear in that registry, its model class must be imported at least once
  before Alembic runs `env.py`.

  By importing every model here, any file that does:
      from app.models import User, Task, ...
  or simply:
      import app.models
  guarantees that ALL tables are registered with Base.metadata — which means
  Alembic will detect schema changes across the entire project.
"""

from app.models.user import User
from app.models.task import Task
from app.models.category import Category
from app.models.tag import Tag, task_tags
from app.models.comment import Comment
from app.models.activity import TaskActivity

# 📌 __all__ controls what `from app.models import *` exports.
# Listing models explicitly here also serves as a quick reference of all
# database entities in the project.
__all__ = ["User", "Task", "Category", "Tag", "task_tags", "Comment", "TaskActivity"]
