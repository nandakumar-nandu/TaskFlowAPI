# -*- coding: utf-8 -*-
"""
🛣️ AUTHENTICATION ROUTES (auth.py)
---------------------------------
Implements API endpoints for user registration, token generation (login),
and current profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, verify_token
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 🔒 Initialize HTTPBearer authentication scheme
security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    🔒 FastAPI Dependency: Retrieve the currently authenticated user.

    This function extracts the JWT bearer token from the Authorization header,
    decodes it, and fetches the corresponding User object from the database.

    Raises:
        HTTPException (401): If the token is missing, invalid, expired, or the user is not found.
        HTTPException (403): If the user's account has been deactivated.

    Returns:
        User: The SQLAlchemy ORM User instance for the logged-in user.
    """
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ⚙️ Query database for the user details
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
        
    return user


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    🛣️ POST /auth/register

    Creates a new user account.

    Validates that the provided email is not already registered. The plain-text
    password is cryptographically hashed using bcrypt before saving to the database.

    Returns:
        UserRead: The newly created user's profile metadata.
    """
    # ⚙️ Check if a user with this email already exists
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # 🔒 Hash the plain password before saving
    hashed_pwd = hash_password(user_in.password)
    
    # ⚙️ Create user instance
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        full_name=user_in.full_name,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    🛣️ POST /auth/login

    Authenticates user credentials and issues a JWT access token.

    Verifies the submitted email exists and the password matches the stored bcrypt hash.
    Generates a signed JWT with a short expiration window (configured in settings).

    Returns:
        Token: A JSON payload containing the `access_token` and `token_type` ("bearer").
    """
    # ⚙️ Fetch user by email
    stmt = select(User).where(User.email == credentials.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # 🔒 Validate existence and verify password
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
        
    # 🔒 Issue JWT access token containing user's UUID string
    token_payload = {"sub": str(user.id)}
    access_token = create_access_token(data=token_payload)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    🛣️ GET /auth/me

    Retrieves profile information for the currently authenticated user.

    Since the `get_current_user` dependency already fetches the user from the
    database, this route simply returns that pre-fetched User object directly.

    Returns:
        UserRead: The authenticated user's profile metadata.
    """
    return current_user
