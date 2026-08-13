# -*- coding: utf-8 -*-
"""
🚨 CENTRALIZED EXCEPTIONS (exceptions.py)
---------------------------------------
Defines domain-specific exceptions to replace generic HTTPExceptions.
"""

from fastapi import HTTPException, status

class TaskNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

class TaskForbiddenError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this task")

class CategoryNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

class CategoryForbiddenError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this category")

class CommentNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

class CommentForbiddenError(HTTPException):
    def __init__(self, detail="You do not have permission to edit this comment"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

class DuplicateEmailError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

class FileTooLargeError(HTTPException):
    def __init__(self, detail="File too large"):
        super().__init__(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=detail)

class InvalidFileTypeError(HTTPException):
    def __init__(self, detail="Invalid file type"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
