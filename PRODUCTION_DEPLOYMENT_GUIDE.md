"""
Production deployment and best practices guide.

Complete guide for deploying the authentication system to production.
"""

"""
PRODUCTION DEPLOYMENT GUIDE
=============================

This guide covers deploying the FastAPI authentication system to production
with security, performance, and reliability best practices.

PRODUCTION CHECKLIST
====================

Security
---------
[ ] Generate strong SECRET_KEY using secrets module (not development key)
[ ] Set ENVIRONMENT=production
[ ] Enable HTTPS/TLS with valid certificate
[ ] Configure CORS for specific frontend domain only
[ ] Implement rate limiting on auth endpoints
[ ] Set up request logging and monitoring
[ ] Implement CSRF protection if needed
[ ] Add security headers (HSTS, X-Frame-Options, etc.)
[ ] Review and test authentication flow end-to-end
[ ] Set up token blacklist (Redis) for logout
[ ] Implement password strength requirements
[ ] Add account lockout after failed attempts
[ ] Monitor failed login attempts

Database
--------
[ ] Use PostgreSQL (not SQLite)
[ ] Configure connection pooling (pool_size, max_overflow)
[ ] Enable SSL for database connection
[ ] Set up automated backups
[ ] Test backup/restore process
[ ] Configure query logging for debugging
[ ] Set up database monitoring
[ ] Use read replicas if needed
[ ] Encrypt sensitive data at rest
[ ] Regularly review and update database indexes

Application
-----------
[ ] Use Uvicorn with multiple workers
[ ] Deploy behind reverse proxy (Nginx, HAProxy)
[ ] Configure proper logging
[ ] Set up log aggregation (ELK, Datadog, etc.)
[ ] Monitor application metrics (CPU, memory, requests)
[ ] Set up error tracking (Sentry, Rollbar)
[ ] Configure automatic restarts
[ ] Use process manager (systemd, supervisor)
[ ] Implement graceful shutdown
[ ] Monitor disk space
[ ] Set up alerts for critical metrics

API
---
[ ] Implement API versioning (/api/v1/)
[ ] Document all endpoints
[ ] Set up API rate limiting
[ ] Implement request/response validation
[ ] Add request ID for tracking
[ ] Set up request timeout handling
[ ] Implement pagination for list endpoints
[ ] Add caching where appropriate
[ ] Monitor API performance
[ ] Track API usage per user/app

Deployment Infrastructure
--------------------------
[ ] Choose deployment platform (AWS, GCP, Azure, etc.)
[ ] Set up CI/CD pipeline
[ ] Configure automated testing on deployment
[ ] Use container orchestration (Kubernetes, Docker Swarm)
[ ] Implement blue-green or canary deployments
[ ] Set up load balancing
[ ] Configure auto-scaling
[ ] Implement health checks
[ ] Set up monitoring and alerting
[ ] Document deployment process

ENVIRONMENT CONFIGURATION
==========================

Production .env file:

# Application
ENVIRONMENT=production
APP_NAME=Team Task Manager
APP_VERSION=1.0.0

# Database
DATABASE_URL=postgresql+psycopg2://prod_user:STRONG_PASSWORD@prod-db.example.com:5432/prod_db

# Security (Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=generated-long-random-string-here-use-secrets-module

# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15        # Shorter in production
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Hashing
BCRYPT_ROUNDS=12

# Email Configuration (for notifications)
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SENDER_EMAIL=noreply@yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/app/app.log

# External Services
REDIS_URL=redis://redis.example.com:6379/0  # For token blacklist, caching
SENTRY_DSN=https://key@sentry.io/project-id
"""

# DATABASE CONFIGURATION
# =======================

Example production database configuration:

# app/core/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings

# Use QueuePool for better connection management
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool if settings.ENVIRONMENT == "production" else None,
    pool_size=20,                    # Number of connections to keep in pool
    max_overflow=40,                 # Additional connections when needed
    pool_recycle=3600,               # Recycle connections every hour
    pool_pre_ping=True,              # Test connection before using
    echo=False if settings.ENVIRONMENT == "production" else True,
    connect_args={
        "timeout": 30,
        "connect_timeout": 10,
        "application_name": "team_task_manager",
    }
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# SSL for database
if settings.ENVIRONMENT == "production":
    event.listen(engine, "connect", lambda dbapi_conn, connection_record:
        dbapi_conn.set_isolation_level(0) if hasattr(dbapi_conn, 'set_isolation_level') else None
    )

UVICORN DEPLOYMENT
==================

Production-ready Uvicorn configuration:

# Command line
uvicorn app.main:app \\
    --host 0.0.0.0 \\
    --port 8000 \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --log-level info \\
    --access-log \\
    --use-colors

# Or use gunicorn with Uvicorn workers (recommended)
gunicorn app.main:app \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 0.0.0.0:8000 \\
    --log-level info \\
    --access-logfile - \\
    --error-logfile - \\
    --timeout 120

# Systemd service file (/etc/systemd/system/fastapi-app.service)
[Unit]
Description=FastAPI Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=appuser
WorkingDirectory=/app
Environment="PATH=/app/venv/bin"
ExecStart=/app/venv/bin/gunicorn app.main:app \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind unix:/tmp/fastapi.sock \\
    --log-level info
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

NGINX REVERSE PROXY
===================

Nginx configuration for production:

# /etc/nginx/sites-available/fastapi-app
upstream fastapi_app {
    server unix:/tmp/fastapi.sock fail_timeout=0;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self'" always;
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Auth endpoints rate limiting
    location /auth/ {
        limit_req zone=auth_limit burst=10 nodelay;
        proxy_pass http://fastapi_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API endpoints rate limiting
    location /api/ {
        limit_req zone=api_limit burst=50 nodelay;
        proxy_pass http://fastapi_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Other endpoints
    location / {
        proxy_pass http://fastapi_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    # Static files (if any)
    location /static/ {
        alias /app/static/;
        expires 30d;
    }
}

LOGGING AND MONITORING
=======================

Production logging configuration:

# app/core/logging_config.py
import logging
import logging.handlers
from pathlib import Path

def setup_logging():
    # Create logs directory
    log_dir = Path("/var/log/app")
    log_dir.mkdir(exist_ok=True)
    
    # Main logger
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    
    # File handler (rotated)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=10,
    )
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Main.py
from app.core.logging_config import setup_logging

logger = setup_logging()

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

MONITORING METRICS
==================

Key metrics to monitor:

1. Authentication Metrics
   - Login attempts (successful and failed)
   - Registration attempts
   - Token refresh count
   - Failed password changes
   - Account lockouts

2. Performance Metrics
   - Response time for auth endpoints
   - Database query time
   - Bcrypt hashing time
   - JWT encoding/decoding time

3. Error Metrics
   - Authentication failures rate
   - Database connection errors
   - Expired token count
   - Invalid token count

4. Security Metrics
   - Brute force attempts
   - Multiple failed logins from same IP
   - Token blacklist size
   - Account deactivations

Example with Prometheus:

# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Counters
login_attempts_total = Counter(
    'login_attempts_total',
    'Total login attempts',
    ['status']  # success, failure, invalid_email, etc.
)

registration_attempts_total = Counter(
    'registration_attempts_total',
    'Total registration attempts',
    ['status']
)

# Histograms
password_hash_duration_seconds = Histogram(
    'password_hash_duration_seconds',
    'Time to hash password'
)

token_decode_duration_seconds = Histogram(
    'token_decode_duration_seconds',
    'Time to decode token'
)

# Usage
from app.core.metrics import login_attempts_total, password_hash_duration_seconds

@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, credentials.email, credentials.password)
        if user:
            login_attempts_total.labels(status="success").inc()
        else:
            login_attempts_total.labels(status="failure").inc()
    except Exception as e:
        login_attempts_total.labels(status="error").inc()

BACKUP AND DISASTER RECOVERY
=============================

Database Backup Strategy:

1. Daily automated backups
2. Backup retention: 30 days
3. Store backups in separate location
4. Test restore process monthly
5. Document recovery procedure

# Backup script (backup.sh)
#!/bin/bash

BACKUP_DIR="/backups/database"
DB_NAME="team_task_manager"
DB_USER="postgres"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Full backup
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/backup_full_$DATE.sql.gz

# Retain only last 30 days
find $BACKUP_DIR -name "backup_full_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_full_$DATE.sql.gz"

# Add to crontab for daily backups
# 0 2 * * * /app/scripts/backup.sh

SCALING AND PERFORMANCE
=======================

Horizontal Scaling:

1. Load Balancing
   - Use HAProxy or AWS ELB
   - Health checks every 10 seconds
   - Connection draining on shutdown

2. Caching Layer
   - Redis for token blacklist
   - Cache user data (1 hour TTL)
   - Cache decoded tokens (5 minutes TTL)

3. Database Optimization
   - Index on email, user_id
   - Denormalize frequently accessed data
   - Archive old sessions/tokens
   - Use read replicas for reads

4. Application Optimization
   - Connection pooling
   - Query optimization
   - Async where possible
   - Batch operations

COST OPTIMIZATION
=================

Cost Reduction Strategies:

1. Reserved Instances (AWS)
   - Commit to 1-3 year terms for 30-50% savings

2. Spot Instances
   - Use for non-critical/batch workloads

3. Database
   - Right-size instance type
   - Use managed services (RDS, Cloud SQL)
   - Enable auto-scaling

4. Monitoring
   - Set budget alerts
   - Track resource usage
   - Remove unused resources regularly

COMPLIANCE AND SECURITY
=======================

Compliance Requirements:

1. GDPR (if EU users)
   - Right to be forgotten
   - Data portability
   - Consent management
   - Privacy policy

2. CCPA (if California users)
   - Similar to GDPR
   - Disclosure requirements

3. SOC 2
   - Access controls
   - Encryption
   - Monitoring
   - Incident response

4. PCI DSS (if handling credit cards)
   - Encryption
   - Access restrictions
   - Regular testing

Security Measures:

# Rate limiting with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    pass

# Request ID for tracking
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(RequestIDMiddleware)

INCIDENT RESPONSE
=================

Security Incident Procedures:

1. Detection
   - Monitor for suspicious activity
   - Alert on anomalies
   - Review logs regularly

2. Response
   - Isolate affected systems
   - Prevent further damage
   - Preserve evidence

3. Recovery
   - Restore from backup
   - Patch vulnerabilities
   - Validate system integrity

4. Communication
   - Notify affected users
   - Document incident
   - Report to authorities if required

Example incident response playbook:

## Incident: Brute Force Attack on Login

Detection:
- Alerting detects 100+ failed logins from same IP in 5 minutes

Response:
1. Block IP immediately (Nginx)
2. Increase login rate limit
3. Enable CAPTCHA on login

Recovery:
1. Review affected accounts
2. Force password reset if needed
3. Enable email notifications

Communication:
1. Email affected users (if any)
2. Post status update
3. Document incident

DISASTER RECOVERY PLAN
======================

Recovery Time Objective (RTO): 4 hours
Recovery Point Objective (RPO): 1 hour

Scenarios:

1. Single Server Failure
   - Automatic failover to standby
   - RTO: 5 minutes
   - Handled by load balancer

2. Database Failure
   - Automatic failover to replica
   - RTO: 1 minute
   - Manual intervention may be needed

3. Data Corruption
   - Restore from latest clean backup
   - RTO: 1 hour
   - RPO: 1 hour

4. Complete System Failure
   - Rebuild from infrastructure-as-code
   - RTO: 4 hours
   - Deploy to backup region/account

Testing:
- Test disaster recovery quarterly
- Document all steps
- Have runbook for each scenario
- Track lessons learned

"""
