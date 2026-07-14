# -*- coding: utf-8 -*-
"""
🔒 SECURITY UTILITIES (security.py)
----------------------------------
🚧 Planned security and authentication helper stubs.
This file will contain functions to hash passwords and generate JWTs in subsequent commits.
"""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    🔒 Verify a plain password against its hashed value.
    🚧 Stub implementation: returns False for now.
    """
    return False


def get_password_hash(password: str) -> str:
    """
    🔒 Generate a secure hash from a plain text password.
    🚧 Stub implementation: returns plain text for now.
    """
    return password


def create_access_token(data: dict) -> str:
    """
    🔒 Generate a signed JSON Web Token (JWT) for user authentication.
    🚧 Stub implementation: returns a mock token.
    """
    return "mock_access_token"
