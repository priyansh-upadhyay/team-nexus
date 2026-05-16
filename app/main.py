from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.teams import router as teams_router
from app.api.team_members import router as team_members_router
from app.api.projects import teams_router as project_teams_router
from app.api.projects import projects_router
from app.api.tasks import projects_router as task_projects_router
from app.api.tasks import tasks_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Team Task Manager backend foundation with JWT authentication",
    version=settings.APP_VERSION,
)

# Set up CORS
origins = [
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Add production origins from settings
if hasattr(settings, "BACKEND_CORS_ORIGINS") and settings.BACKEND_CORS_ORIGINS:
    origins.extend(settings.BACKEND_CORS_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ... (Include routers remains the same)
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(teams_router, prefix="/api")
app.include_router(team_members_router, prefix="/api")
app.include_router(project_teams_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(task_projects_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

@app.get("/api/health-check", tags=["Health"])
def health_check_api() -> dict:
    static_files = []
    if os.path.exists(static_dir):
        static_files = os.listdir(static_dir)
    return {
        "message": "Welcome to the Team Task Manager API",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "static_files": static_files,
        "docs": "/docs",
    }

# ── Static File Serving (Must be at the very end) ──────────────────────────
# Look for 'static' in the current working directory first (common in Docker)
static_dir = os.path.join(os.getcwd(), "static")
if not os.path.exists(static_dir):
    # Fallback to relative path from this file
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

print(f"[INFO] Discovery: Static directory set to: {static_dir}")
print(f"[INFO] Discovery: Static directory exists: {os.path.exists(static_dir)}")
if os.path.exists(static_dir):
    print(f"[INFO] Discovery: Contents of static_dir: {os.listdir(static_dir)}")

if os.path.exists(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        print(f"[INFO] Discovery: Mounting /assets from {assets_dir}")
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Serve the frontend index.html for any route that isn't an API route
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path) and not full_path.startswith("api/"):
            return FileResponse(file_path)
        
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend build files missing. Check /app/static directory."}
else:
    @app.get("/")
    def root():
        return {"message": "Team Task Manager API is running, but static frontend files were not found."}
