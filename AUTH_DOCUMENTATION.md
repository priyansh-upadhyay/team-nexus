"""
Authentication system documentation and quick reference.

This file provides comprehensive documentation for the JWT authentication
system implemented in this FastAPI application.
"""

# AUTHENTICATION SYSTEM DOCUMENTATION
# =====================================

# 1. PROJECT STRUCTURE
# --------------------
# app/
# ├── api/
# │   ├── auth.py              # Authentication endpoints
# │   ├── dependencies.py      # Auth dependency injection
# │   ├── users.py             # Protected user endpoints (example)
# │   └── health.py            # Health check endpoints
# ├── core/
# │   ├── config.py            # Configuration and settings
# │   ├── database.py          # Database session management
# │   └── security.py          # JWT and password utilities
# ├── models/
# │   ├── base.py              # Base SQLAlchemy model
# │   └── user.py              # User model
# ├── schemas/
# │   ├── auth.py              # Pydantic schemas for auth
# │   └── health.py            # Health check schemas
# ├── services/
# │   └── auth.py              # Authentication business logic
# └── main.py                  # FastAPI app setup

# 2. KEY COMPONENTS
# -----------------

# 2.1 SECURITY MODULE (app/core/security.py)
# Functions:
# - hash_password(password) -> str
#   Hashes plaintext password using bcrypt
#
# - verify_password(plain_password, hashed_password) -> bool
#   Verifies plaintext password against bcrypt hash
#
# - create_access_token(data, expires_delta) -> str
#   Creates JWT access token (short-lived, ~30 min)
#
# - create_refresh_token(data) -> str
#   Creates JWT refresh token (long-lived, ~7 days)
#
# - decode_token(token) -> Optional[dict]
#   Decodes and validates JWT token payload

# 2.2 DEPENDENCIES MODULE (app/api/dependencies.py)
# Functions:
# - get_current_user(token, db) -> User
#   FastAPI dependency: validates token and returns authenticated user
#   Use: @app.get("/protected") async def protected(current_user: User = Depends(get_current_user))
#
# - get_current_superuser(current_user) -> User
#   FastAPI dependency: ensures user is superuser
#   Use: @app.delete("/admin") async def admin(current_user: User = Depends(get_current_superuser))
#
# - get_current_active_user(current_user) -> User
#   FastAPI dependency: ensures user account is active

# 2.3 AUTH SERVICE (app/services/auth.py)
# Methods:
# - AuthService.register_user(db, user_create) -> User
#   Creates new user with hashed password
#
# - AuthService.authenticate_user(db, email, password) -> Optional[User]
#   Validates email/password combination
#
# - AuthService.get_user_by_id(db, user_id) -> Optional[User]
# - AuthService.get_user_by_email(db, email) -> Optional[User]
#   Retrieves user from database
#
# - AuthService.create_tokens(user_id) -> Token
#   Generates access and refresh tokens
#
# - AuthService.change_password(db, user, current_password, new_password) -> bool
#   Changes user password with verification

# 2.4 AUTH ENDPOINTS (app/api/auth.py)
# Routes:
# POST /auth/register - Register new user
# POST /auth/login - Login with email/password
# POST /auth/login/oauth2 - OAuth2 password flow (Swagger compatible)
# POST /auth/refresh - Refresh access token
# GET /auth/me - Get current user profile
# POST /auth/change-password - Change user password
# POST /auth/logout - Logout (placeholder)

# 3. AUTHENTICATION FLOW
# ----------------------

# REGISTRATION FLOW:
# 1. Client sends: POST /auth/register { email, full_name, password }
# 2. Server validates input with Pydantic schema
# 3. Server checks if email already registered
# 4. Server hashes password with bcrypt
# 5. Server saves user to database
# 6. Server creates access and refresh tokens
# 7. Server returns: { access_token, refresh_token, token_type }
# 8. Client stores token (typically in localStorage)

# LOGIN FLOW:
# 1. Client sends: POST /auth/login { email, password }
# 2. Server retrieves user by email
# 3. Server verifies password with bcrypt
# 4. Server checks if user account is active
# 5. Server creates access and refresh tokens
# 6. Server returns: { access_token, refresh_token, token_type }
# 7. Client stores token

# AUTHENTICATED REQUEST FLOW:
# 1. Client sends: Authorization: Bearer <access_token>
# 2. FastAPI extracts token from Authorization header
# 3. oauth2_scheme validates token is present
# 4. get_current_user dependency:
#    a. Decodes JWT token using SECRET_KEY
#    b. Extracts user_id from "sub" claim
#    c. Queries database for user
#    d. Verifies user is active
#    e. Returns user object
# 5. Route handler receives User object and processes request

# TOKEN REFRESH FLOW:
# 1. Client sends: POST /auth/refresh { refresh_token }
# 2. Server validates refresh token is valid and not expired
# 3. Server verifies token type is "refresh"
# 4. Server creates new access and refresh tokens
# 5. Server returns: { access_token, refresh_token, token_type }
# 6. Client stores new tokens

# 4. USAGE EXAMPLES
# -----------------

# EXAMPLE 1: Protecting a route
# ----
# from fastapi import APIRouter, Depends
# from app.api.dependencies import get_current_user
# from app.models.user import User
#
# @app.get("/me")
# async def get_profile(current_user: User = Depends(get_current_user)):
#     return current_user

# EXAMPLE 2: Superuser-only route
# ----
# from app.api.dependencies import get_current_superuser
#
# @app.delete("/users/{user_id}")
# async def delete_user(user_id: int, current_user: User = Depends(get_current_superuser)):
#     # Only superusers can delete users
#     db.query(User).filter(User.id == user_id).delete()
#     db.commit()
#     return {"detail": "User deleted"}

# EXAMPLE 3: Manual token creation
# ----
# from app.services.auth import AuthService
# from app.core.database import SessionLocal
#
# db = SessionLocal()
# user = AuthService.authenticate_user(db, "user@example.com", "password123")
# if user:
#     tokens = AuthService.create_tokens(user.id)
#     print(tokens.access_token)

# EXAMPLE 4: Client-side usage (JavaScript/TypeScript)
# ----
# // Register
# const response = await fetch('/auth/register', {
#   method: 'POST',
#   headers: { 'Content-Type': 'application/json' },
#   body: JSON.stringify({
#     email: 'user@example.com',
#     full_name: 'John Doe',
#     password: 'securepassword123'
#   })
# });
# const data = await response.json();
# localStorage.setItem('access_token', data.access_token);
# localStorage.setItem('refresh_token', data.refresh_token);
#
# // Make authenticated request
# const profileResponse = await fetch('/auth/me', {
#   headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
# });
# const profile = await profileResponse.json();

# 5. SECURITY BEST PRACTICES
# ---------------------------

# ✓ IMPLEMENTED:
# - Passwords hashed with bcrypt (12 rounds by default)
# - JWT tokens use HS256 algorithm
# - Access tokens expire in 30 minutes
# - Refresh tokens expire in 7 days
# - User account can be deactivated
# - Superuser flag for role-based access
# - OAuth2 password bearer scheme
# - Email uniqueness constraint
# - Input validation with Pydantic

# ⚠️ PRODUCTION CONSIDERATIONS:

# 1. ENVIRONMENT VARIABLES
#    - Use strong SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
#    - Keep SECRET_KEY secret and rotated
#    - Use different SECRET_KEY per environment
#
# 2. HTTPS/TLS
#    - Always use HTTPS in production
#    - Never send tokens over unencrypted connections
#
# 3. TOKEN MANAGEMENT
#    - Implement token blacklist for logout (use Redis)
#    - Consider storing token revocation list
#    - Set shorter token expiration for sensitive operations
#
# 4. PASSWORD REQUIREMENTS
#    - Enforce strong password policies (minimum 8 chars in schema)
#    - Consider password complexity requirements
#    - Implement account lockout after failed login attempts
#
# 5. RATE LIMITING
#    - Add rate limiting to auth endpoints (prevent brute force)
#    - Use FastAPI-Limiter or similar
#
# 6. AUDIT LOGGING
#    - Log failed login attempts
#    - Log password changes
#    - Log token generation
#
# 7. CORS CONFIGURATION
#    - Configure CORS properly for your frontend domain
#    - Don't use wildcards in production
#
# 8. DATABASE SECURITY
#    - Use connection pooling
#    - Encrypt sensitive data at rest
#    - Implement backups

# 6. CONFIGURATION
# ----------------
# Edit .env file:

# SECRET_KEY=your-secret-key-here
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# REFRESH_TOKEN_EXPIRE_DAYS=7
# BCRYPT_ROUNDS=12

# ACCESS_TOKEN_EXPIRE_MINUTES: How long access tokens are valid (minutes)
#   - Shorter = more secure, more refresh needed
#   - Longer = less secure, fewer refreshes
#   - Typical: 15-60 minutes
#
# REFRESH_TOKEN_EXPIRE_DAYS: How long refresh tokens are valid (days)
#   - Shorter = user re-login more often
#   - Longer = more convenient but less secure
#   - Typical: 7-30 days
#
# BCRYPT_ROUNDS: Security parameter for bcrypt hashing
#   - Higher = slower but more secure
#   - Lower = faster but less secure
#   - Typical: 10-12 rounds
#   - Each increment ~doubles hashing time

# 7. COMMON TASKS
# ---------------

# CREATE ADMIN USER:
# 1. Start Python shell in project:
#    python
# 2. Import and setup:
#    from app.core.database import SessionLocal
#    from app.services.auth import AuthService
#    from app.schemas.auth import UserCreate
#    db = SessionLocal()
# 3. Create admin:
#    admin = AuthService.register_user(db, UserCreate(
#        email="admin@example.com",
#        full_name="Admin User",
#        password="securepassword123"
#    ))
#    admin.is_superuser = True
#    db.commit()

# RESET USER PASSWORD:
# 1. In Python shell:
#    from app.core.security import hash_password
#    user = db.query(User).filter(User.email == "user@example.com").first()
#    user.hashed_password = hash_password("newpassword123")
#    db.commit()

# DEACTIVATE USER:
#    user = db.query(User).filter(User.email == "user@example.com").first()
#    user.is_active = False
#    db.commit()

# 8. TESTING
# ----------

# Using Swagger UI (Automatic):
# 1. Start server: uvicorn app.main:app --reload
# 2. Go to: http://localhost:8000/docs
# 3. Click "Authorize" button
# 4. Use /auth/register to create account
# 5. Use /auth/login to get tokens
# 6. Click "Authorize" and paste access_token
# 7. Try protected endpoints

# Using curl:
# 1. Register:
#    curl -X POST "http://localhost:8000/auth/register" \
#      -H "Content-Type: application/json" \
#      -d '{"email":"test@example.com","full_name":"Test User","password":"testpass123"}'
#
# 2. Login:
#    curl -X POST "http://localhost:8000/auth/login" \
#      -H "Content-Type: application/json" \
#      -d '{"email":"test@example.com","password":"testpass123"}'
#
# 3. Access protected route:
#    curl -X GET "http://localhost:8000/auth/me" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 9. DATABASE MIGRATIONS
# ----------------------
# After changes to User model, create migration:
# alembic revision --autogenerate -m "Add User table"
# alembic upgrade head

# 10. TROUBLESHOOTING
# -------------------

# "Could not validate credentials" error:
# - Token expired: Use refresh endpoint to get new token
# - Token invalid: Check SECRET_KEY matches between server and token creation
# - Token missing: Ensure Authorization header is included
# - Wrong format: Must be "Authorization: Bearer <token>" not "Authorization: <token>"

# "Email already registered" error:
# - User already exists with that email
# - Use different email or login instead

# "User account is inactive" error:
# - User.is_active is False
# - Admin must activate user

# "Incorrect email or password" error:
# - Email doesn't exist or password is wrong
# - Check email spelling
# - Try password reset or create new account

# Password mismatch during change:
# - Current password verification failed
# - Ensure current password is correct
# - Try login first to verify credentials

# 11. API REFERENCE
# -----------------

# POST /auth/register
# Request: { email, full_name, password }
# Response: { access_token, refresh_token, token_type }
# Errors: 400 (email exists), 422 (invalid input)

# POST /auth/login
# Request: { email, password }
# Response: { access_token, refresh_token, token_type }
# Errors: 401 (invalid credentials)

# POST /auth/login/oauth2 (form-data)
# Request: username, password
# Response: { access_token, refresh_token, token_type }
# Errors: 401 (invalid credentials)

# POST /auth/refresh
# Request: { refresh_token }
# Response: { access_token, refresh_token, token_type }
# Errors: 401 (invalid refresh token)

# GET /auth/me
# Headers: Authorization: Bearer <access_token>
# Response: { id, email, full_name, is_active, is_superuser }
# Errors: 401 (not authenticated), 403 (inactive user)

# POST /auth/change-password
# Headers: Authorization: Bearer <access_token>
# Request: { current_password, new_password }
# Response: { detail }
# Errors: 400 (wrong current password), 401 (not authenticated)

# GET /users/me
# Headers: Authorization: Bearer <access_token>
# Response: { id, email, full_name, is_active, is_superuser }
# Errors: 401 (not authenticated)

# GET /users/
# Headers: Authorization: Bearer <access_token>
# Query: skip=0, limit=100
# Response: [{ id, email, full_name, is_active, is_superuser }, ...]
# Errors: 401 (not authenticated), 403 (not superuser)

# GET /users/{user_id}
# Headers: Authorization: Bearer <access_token>
# Response: { id, email, full_name, is_active, is_superuser }
# Errors: 401 (not authenticated), 403 (not superuser), 404 (user not found)

# POST /users/{user_id}/activate
# Headers: Authorization: Bearer <access_token>
# Response: { detail }
# Errors: 401 (not authenticated), 403 (not superuser), 404 (user not found)

# POST /users/{user_id}/deactivate
# Headers: Authorization: Bearer <access_token>
# Response: { detail }
# Errors: 401 (not authenticated), 403 (not superuser), 404 (user not found)
