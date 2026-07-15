# -*- coding: utf-8 -*-
"""
🔒 SECURITY & CRYTOGRAPHY UTILITIES (security.py)
-----------------------------------------------
Provides cryptographic helpers for password hashing (using bcrypt)
and JSON Web Tokens (JWT) creation/verification (using PyJWT).
"""

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import settings


def hash_password(password: str) -> str:
    """
    🔒 Securely hash a plain text password.
    Uses the 'bcrypt' library which automatically handles salting (gensalt) and stretching.
    """
    # ⚙️ Convert plain password to bytes, generate salt, hash it, and decode back to string
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    🔒 Verify a plain text password against a secure bcrypt hash.
    Uses 'bcrypt.checkpw' to resist timing attacks.
    """
    try:
        # ⚙️ Encode string inputs to byte arrays for comparison
        plain_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        # ❌ Handle invalid formats or exceptions safely
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    🔒 Create and sign a JSON Web Token (JWT) using PyJWT.
    Supports a custom token expiration delta, falling back to application defaults.
    """
    to_encode = data.copy()
    
    # ⚙️ Set expiration timestamp (standard claims 'exp')
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp())})
    
    # ⚙️ Encode and sign the JWT payload using the configured algorithm
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    🔒 Decode and cryptographically verify a JWT access token.
    Returns the decoded token claims payload on success, or None if expired/invalid.
    """
    try:
        # ⚙️ Decode token using the application's shared secret key and algorithm
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        # ❌ Token has expired, has an invalid signature, or was malformed
        return None
