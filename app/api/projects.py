"""
Projects API endpoints.

All routes are protected and require a valid JWT token.
Create/update/delete operations are restricted to the team owner.
Viewing is allowed for any team member or owner.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project import ProjectService
from app.services.team import TeamService
from app.services.team_member import TeamMemberService
from app.api.dependencies import get_current_active_user

# Nested under /teams/{team_id}/projects
teams_router = APIRouter(
    prefix="/teams",
    tags=["Projects"],
    responses={401: {"description": "Unauthorized"}},
)

# Standalone /projects/{project_id}
projects_router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    responses={401: {"description": "Unauthorized"}},
)

@projects_router.get(
    "/",
    response_model=List[ProjectResponse],
    summary="List all projects across teams",
)
async def list_all_projects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[ProjectResponse]:
    """Retrieve all projects across all teams the user belongs to."""
    return ProjectService.get_user_projects(db, current_user.id)


@projects_router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
async def create_project_global(
    project_create: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Create a new project. The user must be the team owner."""
    _require_team_owner(db, project_create.team_id, current_user)
    return ProjectService.create_project(db, project_create, project_create.team_id)


def _require_team_access(db: Session, team_id: int, current_user: User) -> None:
    """Raise 403/404 if the team does not exist or the user has no access."""
    team = TeamService.get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    is_owner = team.owner_id == current_user.id
    is_member = TeamMemberService.get_membership(db, team_id, current_user.id) is not None
    if not is_owner and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return team


def _require_team_owner(db: Session, team_id: int, current_user: User) -> None:
    """Raise 403/404 if the team does not exist or the user is not the owner."""
    team = TeamService.get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return team


# ── Team-scoped routes ────────────────────────────────────────────────────────

@teams_router.post(
    "/{team_id}/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project under a team",
    responses={
        201: {"description": "Project created successfully"},
        403: {"description": "Not the team owner"},
        404: {"description": "Team not found"},
    },
)
async def create_project(
    team_id: int,
    project_create: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """
    Create a new project under the specified team.

    **Protected Route:** Only the team owner can create projects.

    **Parameters:**
    - **name**: Project name (required, max 100 characters)
    - **description**: Optional project description
    - **status**: Project status (default: active)

    **Errors:**
    - 403: Authenticated user is not the team owner
    - 404: Team not found
    """
    _require_team_owner(db, team_id, current_user)
    return ProjectService.create_project(db, project_create, team_id)


@teams_router.get(
    "/{team_id}/projects",
    response_model=List[ProjectResponse],
    summary="List all projects for a team",
    responses={
        200: {"description": "Projects retrieved successfully"},
        403: {"description": "Not a team member or owner"},
        404: {"description": "Team not found"},
    },
)
async def list_projects(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[ProjectResponse]:
    """
    Retrieve all projects belonging to a team.

    **Protected Route:** Any team member or owner can view projects.

    **Errors:**
    - 403: Authenticated user is not a member or owner of this team
    - 404: Team not found
    """
    _require_team_access(db, team_id, current_user)
    return ProjectService.get_projects_for_team(db, team_id)


# ── Project-scoped routes ─────────────────────────────────────────────────────

@projects_router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project by ID",
    responses={
        200: {"description": "Project retrieved successfully"},
        403: {"description": "Not a team member or owner"},
        404: {"description": "Project not found"},
    },
)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """
    Retrieve a specific project by ID.

    **Protected Route:** Any team member or owner can view the project.

    **Errors:**
    - 403: Authenticated user is not a member or owner of the project's team
    - 404: Project not found
    """
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    _require_team_access(db, project.team_id, current_user)
    return project


@projects_router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
    responses={
        200: {"description": "Project updated successfully"},
        403: {"description": "Not the team owner"},
        404: {"description": "Project not found"},
    },
)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """
    Update a project's name, description, or status.

    **Protected Route:** Only the team owner can update projects.

    **Errors:**
    - 403: Authenticated user is not the team owner
    - 404: Project not found
    """
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    _require_team_owner(db, project.team_id, current_user)
    return ProjectService.update_project(db, project, project_update)


@projects_router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    responses={
        204: {"description": "Project deleted successfully"},
        403: {"description": "Not the team owner"},
        404: {"description": "Project not found"},
    },
)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a project permanently.

    **Protected Route:** Only the team owner can delete projects.

    **Errors:**
    - 403: Authenticated user is not the team owner
    - 404: Project not found
    """
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    _require_team_owner(db, project.team_id, current_user)
    ProjectService.delete_project(db, project)
