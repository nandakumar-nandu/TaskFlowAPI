# -*- coding: utf-8 -*-
"""
📝 USER PYDANTIC SCHEMAS (user.py)
--------------------------------
Defines request validation and response schemas for user profiles and authentication.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    """
    📝 Shared base schema for user-related input payloads.

    Not used directly in routes. UserCreate and UserUpdate inherit from this
    to share the email field and its validator.

    Validation rules applied to `email`:
      - Stripped of leading/trailing whitespace.
      - Lowercased for consistent storage (prevents case-collision duplicates).
      - Must contain '@' and a domain '.' (basic format check).
    """
    # 📝 Standard user fields shared across schemas
    email: str = Field(
        ...,
        description="Unique email address of the user used for login and registration.",
        examples=["user@example.com"]
    )
    full_name: Optional[str] = Field(
        None,
        description="Optional full name or display name of the user.",
        examples=["John Doe"]
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """
        🧪 Custom validator for standard email structure checks.
        Ensures the email contains an '@' character and a domain dot '.'.
        """
        # ⚙️ Lowercase and strip whitespace to prevent email collation issues
        cleaned_email = v.strip().lower()
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Email must be a valid format containing '@' and domain dots")
        return cleaned_email


class UserCreate(UserBase):
    """
    📝 Request schema for POST /auth/register.

    Accepts email, full_name (from UserBase), plus a plain-text password.
    The password is validated (min 8 chars) here and then immediately hashed
    by the route handler — the plain text is never stored.
    """
    # 📝 Data required during user registration
    password: str = Field(
        ...,
        description="Secure password. Must be at least 8 characters long.",
        examples=["securepassword123"]
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        🧪 Custom validator for password strength checks.
        Ensures the password is at least 8 characters long.
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseModel):
    """
    📝 Request schema for PATCH /users/me.

    All fields are optional so the client only needs to send the fields they
    want to change. Uses Pydantic's model_dump(exclude_unset=True) pattern in
    the service layer to avoid overwriting fields that were not submitted.
    """
    # 📝 Data structure used for profile updates (all fields optional)
    email: Optional[str] = Field(
        None,
        description="Updated email address of the user.",
        examples=["updated@example.com"]
    )
    password: Optional[str] = Field(
        None,
        description="Updated password of the user (minimum 8 characters).",
        examples=["newsecurepwd456"]
    )
    full_name: Optional[str] = Field(
        None,
        description="Updated full name of the user.",
        examples=["John A. Doe"]
    )
    is_active: Optional[bool] = Field(
        None,
        description="Account active status flag.",
        examples=[True]
    )
    avatar_url: Optional[str] = Field(
        None,
        description="Optional relative URL to the uploaded avatar image.",
        examples=["/media/avatars/7b0a88bf-97cc-44a3-ad6c-9411649b8032.png"]
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned_email = v.strip().lower()
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Email must be a valid format containing '@' and domain dots")
        return cleaned_email

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserRead(UserBase):
    """
    📝 Response schema returned for all user profile endpoints.

    Used as the `response_model` for:
      POST /auth/register → 201 Created
      GET  /auth/me       → 200 OK
      GET  /users/me      → 200 OK
      PATCH /users/me     → 200 OK
      POST /users/me/avatar → 200 OK

    `from_attributes=True` enables Pydantic to read field values directly from
    the SQLAlchemy ORM User object returned by the database session.
    """
    # 📝 Data structure returned in response bodies for user details
    id: uuid.UUID = Field(
        ...,
        description="Unique identifier (UUID) assigned to the user.",
        examples=["7b0a88bf-97cc-44a3-ad6c-9411649b8032"]
    )
    is_active: bool = Field(
        ...,
        description="Indicates if the user's account is currently active.",
        examples=[True]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the user account was created.",
        examples=["2026-07-15T17:23:00Z"]
    )
    avatar_url: Optional[str] = Field(
        None,
        description="Relative URL to the uploaded avatar image.",
        examples=["/media/avatars/7b0a88bf-97cc-44a3-ad6c-9411649b8032.png"]
    )

    # ⚙️ Enable Pydantic v2 ORM mapping compatibility
    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    """
    📝 Response schema returned by POST /auth/login on success.

    Contains the signed JWT access token and its type ('bearer').
    The client must include this token in subsequent authenticated requests
    via the `Authorization: Bearer <token>` HTTP header.
    """
    # 📝 Response payload returned upon successful login
    access_token: str = Field(
        ...,
        description="Cryptographically signed JSON Web Token (JWT) access token.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3YjBhODhiZi05N2NjLTQ0YTMtYWQ2Yy05NDExNjQ5YjgwMzIiLCJleHAiOjE3ODUwMzAzMDZ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="The authorization header authentication protocol type (typically 'bearer').",
        examples=["bearer"]
    )


class UserLogin(BaseModel):
    """
    📝 Request schema for POST /auth/login.

    Accepts plain-text email and password. The route handler verifies the
    password against the stored bcrypt hash and issues a JWT on success.
    """
    # 📝 Request payload required for logging in
    email: str = Field(
        ...,
        description="Registered email address of the user.",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        description="Plain text password of the user.",
        examples=["securepassword123"]
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        cleaned_email = v.strip().lower()
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Email must be a valid format containing '@' and domain dots")
        return cleaned_email

