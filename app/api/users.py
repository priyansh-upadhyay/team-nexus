"""
Users API endpoints - example of protected routes.

Demonstrates proper use of authentication dependencies.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.api.dependencies import get_current_user, get_current_superuser

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={401: {"description": "Unauthorized"}},
)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
    responses={
        200: {"description": "User profile retrieved"},
        401: {"description": "Not authenticated"},
    },
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the profile of the currently authenticated user.
    
    **Protected Route:** Requires valid JWT token in Authorization header
    
    **Example Request:**
    ```
    Authorization: Bearer <your_jwt_token>
    ```
    
    **Returns:**
    - Current user's profile information
    
    **Errors:**
    - 401: Not authenticated or invalid token
    """
    return current_user


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List all users (superuser only)",
    responses={
        200: {"description": "Users list retrieved"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
    },
)
async def list_users(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    """
    List all users in the system.
    
    **Protected Route:** Requires superuser privileges
    
    **Parameters:**
    - **skip**: Number of users to skip for pagination (default: 0)
    - **limit**: Maximum number of users to return (default: 100, max: 1000)
    
    **Returns:**
    - List of all users
    
    **Errors:**
    - 401: Not authenticated
    - 403: User does not have superuser privileges
    """
    if limit > 1000:
        limit = 1000
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID (superuser only)",
    responses={
        200: {"description": "User retrieved"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> User:
    """
    Get a specific user by ID.
    
    **Protected Route:** Requires superuser privileges
    
    **Parameters:**
    - **user_id**: ID of the user to retrieve
    
    **Returns:**
    - User information
    
    **Errors:**
    - 401: Not authenticated
    - 403: User does not have superuser privileges
    - 404: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.post(
    "/{user_id}/activate",
    response_model=dict,
    summary="Activate user (superuser only)",
    responses={
        200: {"description": "User activated"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
    },
)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> dict:
    """
    Activate a user account.
    
    **Protected Route:** Requires superuser privileges
    
    **Parameters:**
    - **user_id**: ID of the user to activate
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 401: Not authenticated
    - 403: User does not have superuser privileges
    - 404: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_active = True
    db.commit()
    
    return {"detail": f"User {user.email} activated"}


@router.post(
    "/{user_id}/deactivate",
    response_model=dict,
    summary="Deactivate user (superuser only)",
    responses={
        200: {"description": "User deactivated"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
    },
)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> dict:
    """
    Deactivate a user account.
    
    **Protected Route:** Requires superuser privileges
    
    **Parameters:**
    - **user_id**: ID of the user to deactivate
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 401: Not authenticated
    - 403: User does not have superuser privileges
    - 404: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_active = False
    db.commit()
    
    return {"detail": f"User {user.email} deactivated"}
