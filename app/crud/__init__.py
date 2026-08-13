"""CRUD (Create, Read, Update, Delete) operations for database models.

This module isolates database query logic from business logic in the services layer.
Benefits:
- Easier to swap ORM frameworks (e.g., SQLAlchemy → Tortoise) in the future.
- Simplifies unit testing (mock crud.* instead of db.query).
- Centralizes common query patterns (e.g., soft deletes, pagination).

"""
from .user import user
from .task import task

__all__ = ["user", "task"]
