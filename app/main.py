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

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(teams_router)
app.include_router(team_members_router)
app.include_router(project_teams_router)
app.include_router(projects_router)
app.include_router(task_projects_router)
app.include_router(tasks_router)


@app.get("/", tags=["Health"])
def root() -> dict:
    return {
        "message": "Welcome to the Team Task Manager API",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }
