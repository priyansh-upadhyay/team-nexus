#!/usr/bin/env python
"""
Utility script for authentication system setup and maintenance.

Run: python auth_utils.py [command]
"""

import secrets
import sys
from pathlib import Path
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.services.auth import AuthService
from app.schemas.auth import UserCreate
from app.models.user import User


def generate_secret_key() -> str:
    """Generate a cryptographically secure secret key for JWT."""
    return secrets.token_urlsafe(32)


def create_admin_user(email: str, full_name: str, password: str) -> None:
    """Create an admin user account."""
    db = SessionLocal()
    try:
        user = AuthService.register_user(
            db,
            UserCreate(email=email, full_name=full_name, password=password),
        )
        user.is_superuser = True
        db.commit()
        print(f"✓ Admin user created: {email}")
        print(f"  ID: {user.id}")
        print(f"  Name: {user.full_name}")
    except ValueError as e:
        print(f"✗ Error: {e}")
    finally:
        db.close()


def create_regular_user(email: str, full_name: str, password: str) -> None:
    """Create a regular user account."""
    db = SessionLocal()
    try:
        user = AuthService.register_user(
            db,
            UserCreate(email=email, full_name=full_name, password=password),
        )
        print(f"✓ User created: {email}")
        print(f"  ID: {user.id}")
        print(f"  Name: {user.full_name}")
    except ValueError as e:
        print(f"✗ Error: {e}")
    finally:
        db.close()


def list_users() -> None:
    """List all users in the system."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found.")
            return
        
        print(f"\n{'ID':<5} {'Email':<30} {'Name':<25} {'Active':<7} {'Admin':<7}")
        print("-" * 75)
        for user in users:
            print(
                f"{user.id:<5} {user.email:<30} {user.full_name:<25} "
                f"{'✓' if user.is_active else '✗':<7} {'✓' if user.is_superuser else '✗':<7}"
            )
    finally:
        db.close()


def activate_user(user_id: int) -> None:
    """Activate a user account."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"✗ User {user_id} not found")
            return
        
        user.is_active = True
        db.commit()
        print(f"✓ User {user.email} activated")
    finally:
        db.close()


def deactivate_user(user_id: int) -> None:
    """Deactivate a user account."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"✗ User {user_id} not found")
            return
        
        user.is_active = False
        db.commit()
        print(f"✓ User {user.email} deactivated")
    finally:
        db.close()


def reset_password(user_id: int, new_password: str) -> None:
    """Reset a user's password."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"✗ User {user_id} not found")
            return
        
        user.hashed_password = hash_password(new_password)
        db.commit()
        print(f"✓ Password reset for {user.email}")
    finally:
        db.close()


def promote_to_admin(user_id: int) -> None:
    """Promote a user to admin/superuser."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"✗ User {user_id} not found")
            return
        
        user.is_superuser = True
        db.commit()
        print(f"✓ {user.email} promoted to superuser")
    finally:
        db.close()


def demote_from_admin(user_id: int) -> None:
    """Demote a user from admin/superuser."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"✗ User {user_id} not found")
            return
        
        user.is_superuser = False
        db.commit()
        print(f"✓ {user.email} demoted from superuser")
    finally:
        db.close()


def print_help() -> None:
    """Print help message."""
    help_text = """
Authentication System Utility
==============================

Usage: python auth_utils.py [command] [options]

Commands:

  secret-key
    Generate a secure SECRET_KEY for .env file
    Usage: python auth_utils.py secret-key

  create-admin <email> <full_name> <password>
    Create an admin user
    Usage: python auth_utils.py create-admin admin@example.com "Admin User" "password123"

  create-user <email> <full_name> <password>
    Create a regular user
    Usage: python auth_utils.py create-user user@example.com "John Doe" "password123"

  list-users
    List all users in the system
    Usage: python auth_utils.py list-users

  activate <user_id>
    Activate a user account
    Usage: python auth_utils.py activate 1

  deactivate <user_id>
    Deactivate a user account
    Usage: python auth_utils.py deactivate 1

  reset-password <user_id> <new_password>
    Reset a user's password
    Usage: python auth_utils.py reset-password 1 "newpassword123"

  promote <user_id>
    Promote a user to superuser/admin
    Usage: python auth_utils.py promote 2

  demote <user_id>
    Demote a user from superuser/admin
    Usage: python auth_utils.py demote 2

  help
    Show this help message
    Usage: python auth_utils.py help

Examples:

  Generate SECRET_KEY and add to .env:
    python auth_utils.py secret-key

  Create admin user:
    python auth_utils.py create-admin admin@example.com "Administrator" "securepassword"

  List all users:
    python auth_utils.py list-users

  Promote user ID 2 to admin:
    python auth_utils.py promote 2

  Reset password for user ID 1:
    python auth_utils.py reset-password 1 "newpassword123"
"""
    print(help_text)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    if command == "secret-key":
        print("\nGenerated SECRET_KEY:")
        print("-" * 50)
        print(generate_secret_key())
        print("-" * 50)
        print("\nAdd this to your .env file as SECRET_KEY=<value>")
    
    elif command == "create-admin":
        if len(sys.argv) < 5:
            print("Usage: python auth_utils.py create-admin <email> <full_name> <password>")
            return
        create_admin_user(sys.argv[2], sys.argv[3], sys.argv[4])
    
    elif command == "create-user":
        if len(sys.argv) < 5:
            print("Usage: python auth_utils.py create-user <email> <full_name> <password>")
            return
        create_regular_user(sys.argv[2], sys.argv[3], sys.argv[4])
    
    elif command == "list-users":
        list_users()
    
    elif command == "activate":
        if len(sys.argv) < 3:
            print("Usage: python auth_utils.py activate <user_id>")
            return
        activate_user(int(sys.argv[2]))
    
    elif command == "deactivate":
        if len(sys.argv) < 3:
            print("Usage: python auth_utils.py deactivate <user_id>")
            return
        deactivate_user(int(sys.argv[2]))
    
    elif command == "reset-password":
        if len(sys.argv) < 4:
            print("Usage: python auth_utils.py reset-password <user_id> <new_password>")
            return
        reset_password(int(sys.argv[2]), sys.argv[3])
    
    elif command == "promote":
        if len(sys.argv) < 3:
            print("Usage: python auth_utils.py promote <user_id>")
            return
        promote_to_admin(int(sys.argv[2]))
    
    elif command == "demote":
        if len(sys.argv) < 3:
            print("Usage: python auth_utils.py demote <user_id>")
            return
        demote_from_admin(int(sys.argv[2]))
    
    elif command == "help":
        print_help()
    
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
