"""
FastAPI dependency functions for authentication.

Provides OAuth2 security scheme and current user dependency injection.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.services.auth import AuthService

# OAuth2 scheme for Swagger documentation and automatic token handling
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    description="JWT Bearer token for authentication",
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency to get the current authenticated user.
    
    This dependency:
    1. Extracts JWT token from Authorization header
    2. Validates and decodes the token
    3. Retrieves the user from database
    4. Returns the authenticated user
    
    Use with FastAPI's Depends() in route parameters:
        @app.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    
    Args:
        token: JWT token from Authorization header (injected by oauth2_scheme)
        db: Database session (injected by get_db)
        
    Returns:
        Authenticated User object
        
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode and validate token
    payload = decode_token(token)
    if payload is None:
        raise credential_exception
    
    # Extract user_id from token subject (sub)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credential_exception
    
    try:
        user_id = int(user_id)
    except ValueError:
        raise credential_exception
    
    # Retrieve user from database
    user = AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise credential_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency to get the current authenticated superuser.
    
    Use this for admin-only endpoints:
        @app.delete("/users/{user_id}")
        async def delete_user(user_id: int, current_user: User = Depends(get_current_superuser)):
            # Only superusers can delete users
            ...
    
    Args:
        current_user: Current authenticated user (injected by get_current_user)
        
    Returns:
        Authenticated User object if superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Superuser access required.",
        )
    
    return current_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency to ensure user is active.
    
    This is functionally similar to get_current_user but provides explicit
    documentation of active user requirement.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active User object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    return current_user
