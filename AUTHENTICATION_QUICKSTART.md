"""
Quick start guide for the authentication system.

Follow these steps to set up and use authentication in your FastAPI application.
"""

"""
QUICK START GUIDE
=================

1. INSTALL DEPENDENCIES
   $ pip install -r requirements.txt

2. CONFIGURE ENVIRONMENT
   a. Copy .env.example to .env:
      $ cp .env.example .env
   
   b. Edit .env and set values:
      - DATABASE_URL: Your PostgreSQL connection string
      - SECRET_KEY: Generate a secure key (see below)
      - Other settings as needed

3. GENERATE SECRET KEY
   Run this in Python to generate a secure SECRET_KEY:
   
   $ python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   Copy the output to SECRET_KEY in .env

4. CREATE DATABASE AND TABLES
   a. Create the database (if not exists):
      $ createdb team_task_manager
   
   b. Run migrations:
      $ alembic upgrade head

5. CREATE INITIAL ADMIN USER (Optional)
   $ python
   >>> from app.core.database import SessionLocal
   >>> from app.services.auth import AuthService
   >>> from app.schemas.auth import UserCreate
   >>> db = SessionLocal()
   >>> admin = AuthService.register_user(db, UserCreate(
   ...     email="admin@example.com",
   ...     full_name="Admin User",
   ...     password="securepassword123"
   ... ))
   >>> admin.is_superuser = True
   >>> db.commit()
   >>> exit()

6. START THE SERVER
   $ uvicorn app.main:app --reload
   
   Server runs at: http://localhost:8000
   API docs: http://localhost:8000/docs
   ReDoc: http://localhost:8000/redoc

7. TEST AUTHENTICATION
   
   Using Swagger UI (Recommended):
   a. Go to http://localhost:8000/docs
   b. Find the "auth" section
   c. Try /auth/register endpoint:
      {
        "email": "user@example.com",
        "full_name": "John Doe",
        "password": "securepassword123"
      }
   d. You'll get access_token and refresh_token
   e. Click "Authorize" button and paste the access_token
   f. Try other endpoints
   
   Using curl:
   a. Register:
      curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
          "email":"user@example.com",
          "full_name":"John Doe",
          "password":"securepassword123"
        }'
   
   b. Login:
      curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
          "email":"user@example.com",
          "password":"securepassword123"
        }'
   
   c. Use access token:
      curl -X GET "http://localhost:8000/auth/me" \
        -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

8. USING AUTHENTICATION IN YOUR ROUTES
   
   Protect a route with authentication:
   
   from fastapi import APIRouter, Depends
   from app.api.dependencies import get_current_user, get_current_superuser
   from app.models.user import User
   
   router = APIRouter()
   
   # Any authenticated user
   @router.get("/protected")
   async def protected_route(current_user: User = Depends(get_current_user)):
       return {"message": f"Hello {current_user.full_name}"}
   
   # Superuser only
   @router.delete("/admin-action")
   async def admin_action(current_user: User = Depends(get_current_superuser)):
       return {"message": "Admin action performed"}

9. ACCESSING CURRENT USER INFO
   
   Inside any route with get_current_user dependency:
   
   @app.get("/profile")
   async def get_profile(current_user: User = Depends(get_current_user)):
       return {
           "id": current_user.id,
           "email": current_user.email,
           "full_name": current_user.full_name,
           "is_active": current_user.is_active,
           "is_superuser": current_user.is_superuser,
           "created_at": current_user.created_at,
           "updated_at": current_user.updated_at,
       }

10. PRODUCTION DEPLOYMENT CHECKLIST
    
    □ Change ENVIRONMENT to "production"
    □ Generate strong SECRET_KEY (not development key)
    □ Use strong database password
    □ Enable HTTPS/TLS
    □ Set up logging and monitoring
    □ Configure CORS for your frontend domain
    □ Implement rate limiting
    □ Set up database backups
    □ Review security best practices in AUTH_DOCUMENTATION.md
    □ Test authentication flow end-to-end
    □ Review SQL Alchemy connection pooling settings
    □ Monitor failed login attempts
    □ Set up token refresh strategy in frontend

11. COMMON PATTERNS
    
    Pattern: Get user's data
    @app.get("/my-data")
    async def get_my_data(current_user: User = Depends(get_current_user)):
        # Access current_user properties
        return {"owner_id": current_user.id, "owner_email": current_user.email}
    
    Pattern: Check user permissions
    @app.post("/resource")
    async def create_resource(
        data: ResourceCreate,
        current_user: User = Depends(get_current_user)
    ):
        if not current_user.is_superuser and current_user.id != data.owner_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        # Process request
    
    Pattern: Optional authentication
    async def optional_user(
        current_user: User = Depends(get_current_user)
    ) -> Optional[User]:
        return current_user
    
    @app.get("/public")
    async def public_route(user: Optional[User] = None):
        if user:
            return {"message": f"Hello {user.full_name}"}
        return {"message": "Hello anonymous"}

12. TROUBLESHOOTING
    
    Issue: "Could not validate credentials"
    Solution: 
    - Check token is included in Authorization header
    - Verify token format: "Authorization: Bearer <token>"
    - Token may be expired, use /auth/refresh
    - SECRET_KEY mismatch between .env and server
    
    Issue: "Email already registered"
    Solution:
    - Use different email for registration
    - Use /auth/login if user exists
    
    Issue: "Incorrect email or password"
    Solution:
    - Check email spelling
    - Verify password is correct
    - User account may be inactive
    
    Issue: "Not enough permissions"
    Solution:
    - User is not a superuser
    - Only admins can access this endpoint
    
    Issue: Database connection errors
    Solution:
    - Check DATABASE_URL in .env
    - Verify PostgreSQL is running
    - Check database exists: createdb team_task_manager

13. NEXT STEPS
    
    - Add rate limiting to prevent brute force attacks
    - Implement email verification for new accounts
    - Add password reset functionality
    - Implement two-factor authentication
    - Add social login (Google, GitHub, etc.)
    - Set up OAuth2 resource server
    - Implement RBAC (Role-Based Access Control)
    - Add API key authentication for service-to-service
    - Set up token blacklist for logout
    - Monitor and log authentication events
    
14. DOCUMENTATION
    
    - AUTH_DOCUMENTATION.md: Comprehensive authentication guide
    - See inline code comments in:
      - app/core/security.py: Security utilities
      - app/api/dependencies.py: Dependency injection
      - app/api/auth.py: Auth endpoints
      - app/services/auth.py: Business logic
    
15. API ENDPOINTS SUMMARY
    
    POST /auth/register - Create new account
    POST /auth/login - Login and get tokens
    POST /auth/refresh - Get new access token
    GET /auth/me - Get current user profile
    POST /auth/change-password - Change password
    
    GET /users/me - Get current user
    GET /users/ - List all users (admin only)
    GET /users/{id} - Get user by ID (admin only)
    POST /users/{id}/activate - Activate user (admin only)
    POST /users/{id}/deactivate - Deactivate user (admin only)
"""
