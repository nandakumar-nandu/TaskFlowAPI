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
        description="Unique email address of the user used for login and registration."
    )
    full_name: Optional[str] = Field(
        None,
        description="Optional full name or display name of the user."
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
        description="Secure password. Must be at least 8 characters long."
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
        description="Updated email address of the user."
    )
    password: Optional[str] = Field(
        None,
        description="Updated password of the user (minimum 8 characters)."
    )
    full_name: Optional[str] = Field(
        None,
        description="Updated full name of the user."
    )
    is_active: Optional[bool] = Field(
        None,
        description="Account active status flag."
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
        description="Unique identifier (UUID) assigned to the user."
    )
    is_active: bool = Field(
        ...,
        description="Indicates if the user's account is currently active."
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the user account was created."
    )

    # ⚙️ Enable Pydantic v2 ORM mapping compatibility
    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    # 📝 Response payload returned upon successful login
    access_token: str = Field(
        ...,
        description="Cryptographically signed JSON Web Token (JWT) access token."
    )
    token_type: str = Field(
        default="bearer",
        description="The authorization header authentication protocol type (typically 'bearer')."
    )


class UserLogin(BaseModel):
    # 📝 Request payload required for logging in
    email: str = Field(
        ...,
        description="Registered email address of the user."
    )
    password: str = Field(
        ...,
        description="Plain text password of the user."
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        cleaned_email = v.strip().lower()
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Email must be a valid format containing '@' and domain dots")
        return cleaned_email
