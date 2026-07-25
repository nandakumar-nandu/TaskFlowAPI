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

