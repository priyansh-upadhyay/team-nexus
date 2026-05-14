"""
Testing guide for the authentication system with pytest examples.

Complete test suite for all authentication components.
"""

"""
TESTING AUTHENTICATION SYSTEM
==============================

This guide provides pytest examples and best practices for testing
the JWT authentication system.

SETUP
=====

1. Install testing dependencies:
   pip install pytest pytest-asyncio httpx

2. Create tests/conftest.py for fixtures:

   import pytest
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   from fastapi.testclient import TestClient
   from app.main import app
   from app.core.database import Base, get_db
   
   # Use in-memory SQLite for tests
   SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
   
   engine = create_engine(
       SQLALCHEMY_TEST_DATABASE_URL,
       connect_args={"check_same_thread": False},
   )
   
   TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   
   @pytest.fixture(scope="function")
   def db():
       Base.metadata.create_all(bind=engine)
       yield TestingSessionLocal()
       Base.metadata.drop_all(bind=engine)
   
   @pytest.fixture(scope="function")
   def client(db):
       def override_get_db():
           try:
               yield db
           finally:
               db.close()
       
       app.dependency_overrides[get_db] = override_get_db
       yield TestClient(app)
       app.dependency_overrides.clear()

3. Create tests/__init__.py (empty file)

4. Run tests:
   pytest tests/ -v
   pytest tests/ --cov=app  # With coverage

TEST EXAMPLES
=============

tests/test_security.py
"""

import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password_creates_hash(self):
        """Password should be hashed."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > len(password)
    
    def test_same_password_different_hash(self):
        """Same password should produce different hashes (salt)."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_correct_password(self):
        """Should verify correct password."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed)
    
    def test_verify_incorrect_password(self):
        """Should reject incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = hash_password(password)
        
        assert not verify_password(wrong_password, hashed)


class TestTokenCreation:
    """Test JWT token creation and decoding."""
    
    def test_create_access_token(self):
        """Should create a valid access token."""
        token = create_access_token({"sub": "123"})
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Should decode valid token."""
        payload = {"sub": "123"}
        token = create_access_token(payload)
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "123"
        assert decoded["type"] == "access"
    
    def test_decode_invalid_token(self):
        """Should return None for invalid token."""
        invalid_token = "invalid_token_string"
        decoded = decode_token(invalid_token)
        
        assert decoded is None
    
    def test_token_has_expiration(self):
        """Token should have expiration claim."""
        token = create_access_token({"sub": "123"})
        payload = decode_token(token)
        
        assert "exp" in payload
    
    def test_create_refresh_token(self):
        """Should create refresh token with correct type."""
        token = create_refresh_token({"sub": "123"})
        payload = decode_token(token)
        
        assert payload["type"] == "refresh"


# tests/test_auth_endpoints.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.core.security import hash_password


class TestRegistration:
    """Test user registration endpoint."""
    
    def test_register_user_success(self, client):
        """Should register user successfully."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "securepassword123",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_email(self, client, db):
        """Should reject duplicate email."""
        # Create first user
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "securepassword123",
            },
        )
        
        # Try to register same email
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Another User",
                "password": "securepassword123",
            },
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_invalid_email(self, client):
        """Should reject invalid email."""
        response = client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "full_name": "Test User",
                "password": "securepassword123",
            },
        )
        
        assert response.status_code == 422
    
    def test_register_weak_password(self, client):
        """Should reject password less than 8 characters."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "short",
            },
        )
        
        assert response.status_code == 422


class TestLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client):
        """Should login successfully."""
        # Register user first
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "securepassword123",
            },
        )
        
        # Login
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "securepassword123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_login_invalid_email(self, client):
        """Should reject invalid email."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword",
            },
        )
        
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]
    
    def test_login_invalid_password(self, client):
        """Should reject invalid password."""
        # Register user first
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "securepassword123",
            },
        )
        
        # Login with wrong password
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401


class TestProtectedRoutes:
    """Test protected endpoints."""
    
    def test_get_current_user_with_token(self, client):
        """Should get current user with valid token."""
        # Register and login
        register_response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "securepassword123",
            },
        )
        token = register_response.json()["access_token"]
        
        # Access protected route
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
    
    def test_get_current_user_without_token(self, client):
        """Should reject request without token."""
        response = client.get("/auth/me")
        
        assert response.status_code == 403
    
    def test_get_current_user_with_invalid_token(self, client):
        """Should reject invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        
        assert response.status_code == 401
    
    def test_get_current_user_with_wrong_bearer_format(self, client):
        """Should reject wrong Authorization header format."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "invalid_token"},
        )
        
        assert response.status_code == 403


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_refresh_token_success(self, client):
        """Should refresh token successfully."""
        # Register and get tokens
        register_response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "securepassword123",
            },
        )
        refresh_token = register_response.json()["refresh_token"]
        
        # Refresh
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_invalid_token(self, client):
        """Should reject invalid refresh token."""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        
        assert response.status_code == 401


class TestChangePassword:
    """Test password change endpoint."""
    
    def test_change_password_success(self, client):
        """Should change password successfully."""
        # Register
        register_response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "oldpassword123",
            },
        )
        token = register_response.json()["access_token"]
        
        # Change password
        response = client.post(
            "/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword123",
            },
        )
        
        assert response.status_code == 200
        
        # Try login with new password
        login_response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "newpassword123",
            },
        )
        assert login_response.status_code == 200
    
    def test_change_password_wrong_current(self, client):
        """Should reject wrong current password."""
        # Register
        register_response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "correctpassword",
            },
        )
        token = register_response.json()["access_token"]
        
        # Try to change with wrong current password
        response = client.post(
            "/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
            },
        )
        
        assert response.status_code == 400


class TestSuperuserAccess:
    """Test superuser-only endpoints."""
    
    def test_regular_user_cannot_access_admin_endpoint(self, client, db):
        """Regular user should be denied superuser endpoints."""
        # Create regular user
        register_response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "full_name": "Regular User",
                "password": "password123",
            },
        )
        token = register_response.json()["access_token"]
        
        # Try to access admin endpoint
        response = client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_superuser_can_access_admin_endpoint(self, client, db):
        """Superuser should access admin endpoints."""
        # Create superuser directly in DB
        from app.models.user import User
        from app.core.security import hash_password
        
        admin = User(
            email="admin@example.com",
            hashed_password=hash_password("password123"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
        
        # Login as admin
        login_response = client.post(
            "/auth/login/oauth2",
            data={"username": "admin@example.com", "password": "password123"},
        )
        token = login_response.json()["access_token"]
        
        # Access admin endpoint
        response = client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200


RUNNING TESTS
=============

Run all tests:
    pytest tests/ -v

Run specific test file:
    pytest tests/test_auth_endpoints.py -v

Run specific test class:
    pytest tests/test_auth_endpoints.py::TestLogin -v

Run specific test function:
    pytest tests/test_auth_endpoints.py::TestLogin::test_login_success -v

Run with coverage:
    pytest tests/ --cov=app --cov-report=html

Run tests and show print statements:
    pytest tests/ -v -s

Run tests in parallel (requires pytest-xdist):
    pytest tests/ -n auto

COVERAGE TARGETS
================

Target: 90% coverage for authentication system

Key modules to test:
- app/core/security.py (password hashing, token management)
- app/services/auth.py (user registration, authentication)
- app/api/auth.py (all endpoints)
- app/api/dependencies.py (dependency injection)

Run coverage report:
    pytest tests/ --cov=app --cov-report=html
    open htmlcov/index.html

CONTINUOUS INTEGRATION
======================

Example GitHub Actions workflow (.github/workflows/tests.yml):

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: pytest tests/ --cov=app
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2

MOCKING
=======

Example with mocking external services:

import pytest
from unittest.mock import patch, MagicMock


def test_email_verification_called(client):
    \"\"\"Email should be sent during registration.\"\"\"
    with patch('app.services.auth.send_email') as mock_email:
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test",
                "password": "password123",
            },
        )
        
        assert response.status_code == 201
        # Verify email was called
        mock_email.assert_called_once()
        args, kwargs = mock_email.call_args
        assert "test@example.com" in args

PERFORMANCE TESTING
===================

Test authentication performance:

import time


def test_password_hashing_performance():
    \"\"\"Password hashing should complete in reasonable time.\"\"\"
    password = "test_password_123"
    
    start = time.time()
    hashed = hash_password(password)
    duration = time.time() - start
    
    # Should take less than 1 second
    assert duration < 1.0


def test_token_decoding_performance():
    \"\"\"Token decoding should be fast.\"\"\"
    token = create_access_token({"sub": "123"})
    
    start = time.time()
    for _ in range(100):
        decode_token(token)
    duration = time.time() - start
    
    # 100 decodings should take less than 1 second
    assert duration < 1.0
"""
