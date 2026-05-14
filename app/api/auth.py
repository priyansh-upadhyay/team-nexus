"""
Authentication API endpoints.

Provides login, register, token refresh, and profile management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    TokenRefresh,
    PasswordChange,
)
from app.services.auth import AuthService
from app.core.security import decode_token, create_access_token, verify_password, hash_password
from app.api.dependencies import get_current_user, get_current_active_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Email already registered or invalid input"},
    },
)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db),
) -> Token:
    """
    Register a new user account.
    
    **Parameters:**
    - **email**: User's email address (must be unique)
    - **full_name**: User's full name
    - **password**: Password (minimum 8 characters)
    
    **Returns:**
    - Access and refresh tokens for immediate authentication
    
    **Errors:**
    - 400: Email already registered or invalid input
    """
    try:
        user = AuthService.register_user(db, user_create)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return AuthService.create_tokens(user.id)


@router.post(
    "/login",
    response_model=Token,
    summary="Login with email and password",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    """
    Authenticate user with email and password.
    
    **Parameters:**
    - **email**: User's registered email
    - **password**: User's password
    
    **Returns:**
    - Access and refresh tokens for API authentication
    
    **Errors:**
    - 401: Invalid email or password
    """
    user = AuthService.authenticate_user(
        db,
        email=credentials.email,
        password=credentials.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return AuthService.create_tokens(user.id)


@router.post(
    "/login/oauth2",
    response_model=Token,
    summary="Login using OAuth2 password flow",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """
    OAuth2 compatible login endpoint.
    
    This endpoint supports the standard OAuth2 password flow and is used by
    Swagger UI for token generation.
    
    **Parameters (form data):**
    - **username**: User's email address
    - **password**: User's password
    
    **Returns:**
    - Access and refresh tokens
    
    **Errors:**
    - 401: Invalid credentials
    """
    user = AuthService.authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return AuthService.create_tokens(user.id)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid refresh token"},
    },
)
async def refresh_token(
    token_refresh: TokenRefresh,
    db: Session = Depends(get_db),
) -> Token:
    """
    Generate a new access token using a refresh token.
    
    **Parameters:**
    - **refresh_token**: Valid refresh token from login/register
    
    **Returns:**
    - New access token and refresh token pair
    
    **Errors:**
    - 401: Invalid or expired refresh token
    """
    payload = decode_token(token_refresh.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return AuthService.create_tokens(int(user_id))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    responses={
        200: {"description": "User profile retrieved"},
        401: {"description": "Not authenticated"},
    },
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current authenticated user's profile.
    
    **Returns:**
    - Current user's profile information
    
    **Errors:**
    - 401: Not authenticated or invalid token
    - 403: User account is inactive
    """
    return current_user


@router.post(
    "/change-password",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Change user password",
    responses={
        200: {"description": "Password changed successfully"},
        400: {"description": "Invalid current password"},
        401: {"description": "Not authenticated"},
    },
)
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Change the current user's password.
    
    **Parameters:**
    - **current_password**: User's current password for verification
    - **new_password**: New password (minimum 8 characters)
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 400: Current password is incorrect
    - 401: Not authenticated
    """
    try:
        AuthService.change_password(
            db,
            current_user,
            password_change.current_password,
            password_change.new_password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return {"detail": "Password changed successfully"}


@router.post(
    "/logout",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Logout (client-side token removal)",
    responses={
        200: {"description": "Logout successful"},
        401: {"description": "Not authenticated"},
    },
)
async def logout(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Logout endpoint.
    
    **Note:** This is a placeholder endpoint. JWT tokens cannot be revoked
    server-side without a token blacklist. For production, implement:
    - Token blacklist (Redis) to prevent token reuse
    - Shorter token expiration times
    - Client-side token removal
    
    **Returns:**
    - Success message
    """
    return {"detail": "Logout successful. Please remove token from client."}
