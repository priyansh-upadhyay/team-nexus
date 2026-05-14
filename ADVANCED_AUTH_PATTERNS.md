"""
Advanced authentication patterns and testing examples.

This file demonstrates best practices and advanced usage patterns
for the authentication system.
"""

"""
ADVANCED AUTHENTICATION PATTERNS
=================================

1. OPTIONAL AUTHENTICATION
   ========================
   
   Sometimes you want an endpoint that works both for authenticated
   and anonymous users, returning different data based on authentication.
   
   from typing import Optional
   from fastapi import APIRouter, Depends
   from app.api.dependencies import oauth2_scheme
   from app.core.security import decode_token
   from app.models.user import User
   
   async def optional_get_current_user(
       token: Optional[str] = Depends(oauth2_scheme)
   ) -> Optional[User]:
       if token is None:
           return None
       
       payload = decode_token(token)
       if not payload:
           return None
       
       user_id = payload.get("sub")
       # Retrieve user from database...
       return user
   
   @app.get("/products")
   async def list_products(current_user: Optional[User] = Depends(optional_get_current_user)):
       if current_user:
           # Return personalized product recommendations
           return {"products": [...], "personalized": True}
       else:
           # Return general products
           return {"products": [...], "personalized": False}

2. SCOPED PERMISSIONS
   ===================
   
   Implement fine-grained permission checks beyond simple superuser flag.
   
   class PermissionLevel(str, Enum):
       READ = "read"
       WRITE = "write"
       DELETE = "delete"
       ADMIN = "admin"
   
   async def check_permission(
       required_permission: PermissionLevel,
       current_user: User = Depends(get_current_user)
   ) -> User:
       permission_map = {
           PermissionLevel.READ: 0,
           PermissionLevel.WRITE: 1,
           PermissionLevel.DELETE: 2,
           PermissionLevel.ADMIN: 3,
       }
       
       user_level = 3 if current_user.is_superuser else 0
       
       if permission_map[required_permission] > user_level:
           raise HTTPException(status_code=403, detail="Insufficient permissions")
       
       return current_user
   
   @app.delete("/users/{user_id}")
   async def delete_user(
       user_id: int,
       current_user: User = Depends(
           lambda: check_permission(PermissionLevel.ADMIN)
       )
   ):
       # Only admins can delete users
       pass

3. ROLE-BASED ACCESS CONTROL (RBAC)
   =================================
   
   Implement role-based access for more flexible permission management.
   
   class UserRole(str, Enum):
       ADMIN = "admin"
       MODERATOR = "moderator"
       USER = "user"
       GUEST = "guest"
   
   async def require_role(
       required_roles: List[UserRole],
       current_user: User = Depends(get_current_user)
   ) -> User:
       # Store user.role in database
       if current_user.role not in required_roles:
           raise HTTPException(status_code=403, detail="Insufficient permissions")
       return current_user
   
   @app.post("/moderate")
   async def moderate_content(
       current_user: User = Depends(
           lambda: require_role([UserRole.ADMIN, UserRole.MODERATOR])
       )
   ):
       # Only admins and moderators can moderate
       pass

4. TOKEN WITH ADDITIONAL CLAIMS
   =============================
   
   Include additional information in the JWT token for more efficient
   authorization without database queries.
   
   # In auth.py:
   def create_access_token_with_claims(user: User) -> str:
       to_encode = {
           "sub": str(user.id),
           "email": user.email,
           "is_superuser": user.is_superuser,
           "org_id": user.organization_id,  # if applicable
       }
       expire = datetime.utcnow() + timedelta(
           minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
       )
       to_encode.update({"exp": expire})
       
       encoded_jwt = jwt.encode(
           to_encode,
           settings.SECRET_KEY,
           algorithm=settings.ALGORITHM,
       )
       return encoded_jwt
   
   # In dependencies.py:
   async def get_current_user(token: str = Depends(oauth2_scheme)):
       payload = decode_token(token)
       # Use claims from token for faster checks
       is_admin = payload.get("is_superuser", False)
       org_id = payload.get("org_id")

5. MULTI-TENANCY WITH JWT
   =======================
   
   Support multiple organizations in JWT tokens.
   
   def create_access_token_for_tenant(user: User, tenant_id: int) -> str:
       to_encode = {
           "sub": str(user.id),
           "tenant_id": tenant_id,
       }
       # ... rest of implementation
   
   async def get_current_user_in_tenant(
       tenant_id: int,
       current_user: User = Depends(get_current_user)
   ) -> User:
       payload = decode_token(token)
       token_tenant = payload.get("tenant_id")
       
       if token_tenant != tenant_id:
           raise HTTPException(
               status_code=403,
               detail="Access denied to this organization"
           )
       return current_user
   
   @app.get("/orgs/{org_id}/data")
   async def get_org_data(
       org_id: int,
       current_user: User = Depends(
           lambda: get_current_user_in_tenant(org_id)
       )
   ):
       # Only users with access to this organization
       pass

6. TOKEN BLACKLIST FOR LOGOUT
   ============================
   
   Implement token blacklist using Redis for proper logout functionality.
   
   import redis
   
   redis_client = redis.Redis(host='localhost', port=6379)
   
   def logout_token(token: str) -> None:
       payload = decode_token(token)
       if payload:
           exp = payload.get("exp")
           ttl = int(exp - time.time())
           if ttl > 0:
               redis_client.setex(f"blacklist:{token}", ttl, "1")
   
   async def get_current_user_with_blacklist(
       token: str = Depends(oauth2_scheme)
   ) -> User:
       if redis_client.get(f"blacklist:{token}"):
           raise HTTPException(status_code=401, detail="Token has been revoked")
       
       return await get_current_user(token)
   
   @app.post("/auth/logout")
   async def logout(current_user: User = Depends(get_current_user)):
       # This endpoint handles both token and cleanup
       logout_token(token)
       return {"detail": "Logged out successfully"}

7. EMAIL VERIFICATION
   ===================
   
   Require email verification before account can be used.
   
   def send_verification_email(user: User, token: str) -> None:
       verification_url = f"http://yourapp.com/verify-email?token={token}"
       # Send email with verification link
   
   @app.post("/auth/register")
   async def register(user_create: UserCreate, db: Session = Depends(get_db)):
       user = AuthService.register_user(db, user_create)
       user.is_active = False  # Disable until verified
       verification_token = create_access_token({"sub": str(user.id), "type": "verify"})
       send_verification_email(user, verification_token)
       return {"detail": "Registration successful. Check your email to verify."}
   
   @app.get("/auth/verify-email")
   async def verify_email(token: str, db: Session = Depends(get_db)):
       payload = decode_token(token)
       if payload.get("type") != "verify":
           raise HTTPException(status_code=400, detail="Invalid token")
       
       user_id = payload.get("sub")
       user = db.query(User).filter(User.id == user_id).first()
       user.is_active = True
       db.commit()
       return {"detail": "Email verified successfully"}

8. PASSWORD RESET
   ===============
   
   Implement secure password reset flow.
   
   def send_password_reset_email(user: User, token: str) -> None:
       reset_url = f"http://yourapp.com/reset-password?token={token}"
       # Send email with reset link
   
   @app.post("/auth/forgot-password")
   async def forgot_password(email: str, db: Session = Depends(get_db)):
       user = db.query(User).filter(User.email == email).first()
       if not user:
           # Don't reveal if email exists (security best practice)
           return {"detail": "If email exists, reset link sent"}
       
       reset_token = create_access_token({"sub": str(user.id), "type": "reset"})
       send_password_reset_email(user, reset_token)
       return {"detail": "If email exists, reset link sent"}
   
   @app.post("/auth/reset-password")
   async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
       payload = decode_token(token)
       if payload.get("type") != "reset":
           raise HTTPException(status_code=400, detail="Invalid token")
       
       user_id = payload.get("sub")
       user = db.query(User).filter(User.id == user_id).first()
       user.hashed_password = hash_password(new_password)
       db.commit()
       return {"detail": "Password reset successfully"}

9. RATE LIMITING
   ==============
   
   Prevent brute force attacks on auth endpoints.
   
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/auth/login")
   @limiter.limit("5/minute")
   async def login(request: Request, credentials: UserLogin):
       # After 5 login attempts per minute, further requests are blocked
       pass

10. SESSION MANAGEMENT
    ===================
    
    For additional security, track user sessions.
    
    class UserSession(Base):
        __tablename__ = "user_sessions"
        
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey("users.id"))
        token_hash = Column(String, unique=True, index=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        expires_at = Column(DateTime)
        ip_address = Column(String)
        user_agent = Column(String)
        is_active = Column(Boolean, default=True)
    
    def create_session(user_id: int, token: str, request: Request, db: Session):
        token_hash = hash_password(token)
        session = UserSession(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=30),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(session)
        db.commit()

TESTING
=======

1. UNIT TESTING PASSWORD HASHING
   
   from app.core.security import hash_password, verify_password
   
   def test_password_hashing():
       password = "test_password_123"
       hashed = hash_password(password)
       assert hash_password(password) != hashed  # Different hash each time (salt)
       assert verify_password(password, hashed)
       assert not verify_password("wrong_password", hashed)

2. UNIT TESTING TOKEN CREATION
   
   from app.core.security import create_access_token, decode_token
   
   def test_token_creation():
       token = create_access_token({"sub": "123"})
       payload = decode_token(token)
       assert payload["sub"] == "123"
       assert payload["type"] == "access"

3. INTEGRATION TESTING AUTH ENDPOINTS
   
   from fastapi.testclient import TestClient
   from app.main import app
   
   client = TestClient(app)
   
   def test_register():
       response = client.post("/auth/register", json={
           "email": "test@example.com",
           "full_name": "Test User",
           "password": "password123"
       })
       assert response.status_code == 201
       assert "access_token" in response.json()

   def test_login():
       response = client.post("/auth/login", json={
           "email": "test@example.com",
           "password": "password123"
       })
       assert response.status_code == 200
       assert "access_token" in response.json()

   def test_protected_route():
       # First login
       login_response = client.post("/auth/login", json={
           "email": "test@example.com",
           "password": "password123"
       })
       token = login_response.json()["access_token"]
       
       # Then access protected route
       response = client.get(
           "/auth/me",
           headers={"Authorization": f"Bearer {token}"}
       )
       assert response.status_code == 200
       assert response.json()["email"] == "test@example.com"

4. TESTING SUPERUSER ACCESS
   
   def test_superuser_only_endpoint():
       # Regular user
       user_token = get_user_token("user@example.com")
       response = client.get("/users", headers={"Authorization": f"Bearer {user_token}"})
       assert response.status_code == 403
       
       # Superuser
       admin_token = get_admin_token("admin@example.com")
       response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
       assert response.status_code == 200

"""
