"""
Authentication service containing business logic for user management.

Handles user creation, authentication, and token management following DDD principles.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.schemas.auth import UserCreate, Token


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def register_user(db: Session, user_create: UserCreate) -> User:
        """
        Register a new user in the system.
        
        Args:
            db: Database session
            user_create: User creation data
            
        Returns:
            Created User object
            
        Raises:
            ValueError: If email already exists
        """
        # Check if user already exists
        existing_user = db.execute(
            select(User).where(User.email == user_create.email)
        ).scalar_one_or_none()
        
        if existing_user:
            raise ValueError(f"Email {user_create.email} already registered")
        
        # Create new user with hashed password
        db_user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hash_password(user_create.password),
            is_active=True,
            is_superuser=False,
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.
        
        Args:
            db: Database session
            email: User's email address
            password: User's plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.
        
        Args:
            db: Database session
            user_id: User's ID
            
        Returns:
            User object if found, None otherwise
        """
        return db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by email.
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        return db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
    
    @staticmethod
    def create_tokens(user_id: int) -> Token:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user_id: User's ID to encode in token
            
        Returns:
            Token object containing access_token and refresh_token
        """
        access_token = create_access_token(data={"sub": str(user_id)})
        refresh_token = create_refresh_token(data={"sub": str(user_id)})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
    
    @staticmethod
    def change_password(
        db: Session,
        user: User,
        current_password: str,
        new_password: str,
    ) -> bool:
        """
        Change user's password.
        
        Args:
            db: Database session
            user: User object
            current_password: User's current password
            new_password: New password to set
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If current password is incorrect
        """
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        user.hashed_password = hash_password(new_password)
        db.commit()
        
        return True
