"""
Pydantic schemas for authentication endpoints.

Handles request/response validation and serialization.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)"
    )


class UserResponse(UserBase):
    """Schema for returning user information in API responses."""
    
    id: int = Field(..., description="User's unique identifier")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_superuser: bool = Field(..., description="Whether the user has admin privileges")
    
    class Config:
        from_attributes = True  # For SQLAlchemy ORM model conversion


class UserLogin(BaseModel):
    """Schema for user login credentials."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class Token(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="Optional JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")


class TokenData(BaseModel):
    """Schema for decoded token payload data."""
    
    user_id: int = Field(..., description="User ID from token")
    token_type: str = Field(..., description="Type of token (access or refresh)")


class PasswordChange(BaseModel):
    """Schema for changing user password."""
    
    current_password: str = Field(..., description="User's current password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (minimum 8 characters)"
    )


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    
    refresh_token: str = Field(..., description="Valid refresh token")
