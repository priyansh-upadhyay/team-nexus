"""
Tasks API endpoints.

All routes are protected and require a valid JWT token.
Create: team members only.
View: team members only.
Update: team owner OR assigned user.
Delete: team owner only.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task import TaskService
from app.services.project import ProjectService
from app.services.team import TeamService
from app.services.team_member import TeamMemberService
from app.api.dependencies import get_current_active_user

# Nested under /projects/{project_id}/tasks
projects_router = APIRouter(
    prefix="/projects",
    tags=["Tasks"],
    responses={401: {"description": "Unauthorized"}},
)

# Standalone /tasks/{task_id}
tasks_router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={401: {"description": "Unauthorized"}},
)

@tasks_router.get(
    "/",
    response_model=List[TaskResponse],
    summary="List all tasks across projects",
)
async def list_all_tasks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    """Retrieve all tasks across all projects the user has access to."""
    return TaskService.get_user_tasks(db, current_user.id)


@tasks_router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
async def create_task_global(
    task_create: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Create a new task under the specified project."""
    project = _get_project_or_404(db, task_create.project_id)
    _require_team_member_or_owner(db, project.team_id, current_user)

    try:
        return TaskService.create_task(db, task_create, task_create.project_id, project.team_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ── Shared auth helpers ───────────────────────────────────────────────────────

def _get_project_or_404(db: Session, project_id: int):
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


def _get_team_or_404(db: Session, team_id: int):
    team = TeamService.get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    return team


def _require_team_member_or_owner(db: Session, team_id: int, current_user: User):
    """Raise 403 if the user is neither the team owner nor a team member."""
    team = _get_team_or_404(db, team_id)
    is_owner = team.owner_id == current_user.id
    is_member = TeamMemberService.get_membership(db, team_id, current_user.id) is not None
    if not is_owner and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return team


def _require_team_owner(db: Session, team_id: int, current_user: User):
    """Raise 403 if the user is not the team owner."""
    team = _get_team_or_404(db, team_id)
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return team


def _require_owner_or_assignee(db: Session, team_id: int, task, current_user: User):
    """Raise 403 if the user is neither the team owner nor the task assignee."""
    team = _get_team_or_404(db, team_id)
    is_owner = team.owner_id == current_user.id
    is_assignee = task.assignee_id == current_user.id
    if not is_owner and not is_assignee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return team


# ── Project-scoped routes ─────────────────────────────────────────────────────

@projects_router.post(
    "/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task under a project",
    responses={
        201: {"description": "Task created successfully"},
        400: {"description": "Assignee is not a team member"},
        403: {"description": "Not a team member"},
        404: {"description": "Project not found"},
    },
)
async def create_task(
    project_id: int,
    task_create: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Create a new task under the specified project.

    **Protected Route:** Any team member or owner can create tasks.

    **Parameters:**
    - **title**: Task title (required, max 200 characters)
    - **description**: Optional task description
    - **status**: todo | in_progress | review | done (default: todo)
    - **priority**: low | medium | high (default: medium)
    - **assignee_id**: Optional user ID — must be a team member
    - **due_date**: Optional due date (YYYY-MM-DD)

    **Errors:**
    - 400: Assignee does not exist or is not a team member
    - 403: Authenticated user is not a team member or owner
    - 404: Project not found
    """
    project = _get_project_or_404(db, project_id)
    _require_team_member_or_owner(db, project.team_id, current_user)

    try:
        return TaskService.create_task(db, task_create, project_id, project.team_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@projects_router.get(
    "/{project_id}/tasks",
    response_model=List[TaskResponse],
    summary="List all tasks for a project",
    responses={
        200: {"description": "Tasks retrieved successfully"},
        403: {"description": "Not a team member or owner"},
        404: {"description": "Project not found"},
    },
)
async def list_tasks(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    """
    Retrieve all tasks belonging to a project.

    **Protected Route:** Any team member or owner can view tasks.

    **Errors:**
    - 403: Authenticated user is not a member or owner of the project's team
    - 404: Project not found
    """
    project = _get_project_or_404(db, project_id)
    _require_team_member_or_owner(db, project.team_id, current_user)
    return TaskService.get_tasks_for_project(db, project_id)


# ── Task-scoped routes ────────────────────────────────────────────────────────

@tasks_router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    responses={
        200: {"description": "Task retrieved successfully"},
        403: {"description": "Not a team member or owner"},
        404: {"description": "Task not found"},
    },
)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Retrieve a specific task by ID.

    **Protected Route:** Any team member or owner can view the task.

    **Errors:**
    - 403: Authenticated user is not a member or owner of the task's team
    - 404: Task not found
    """
    task = TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    project = _get_project_or_404(db, task.project_id)
    _require_team_member_or_owner(db, project.team_id, current_user)
    return task


@tasks_router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    responses={
        200: {"description": "Task updated successfully"},
        400: {"description": "Assignee is not a team member"},
        403: {"description": "Not the team owner or task assignee"},
        404: {"description": "Task not found"},
    },
)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Update a task's fields.

    **Protected Route:** Team owner OR the currently assigned user can update.

    **Errors:**
    - 400: New assignee does not exist or is not a team member
    - 403: Authenticated user is neither the team owner nor the task assignee
    - 404: Task not found
    """
    task = TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    project = _get_project_or_404(db, task.project_id)
    _require_owner_or_assignee(db, project.team_id, task, current_user)

    try:
        return TaskService.update_task(db, task, task_update, project.team_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@tasks_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    responses={
        204: {"description": "Task deleted successfully"},
        403: {"description": "Not the team owner"},
        404: {"description": "Task not found"},
    },
)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a task permanently.

    **Protected Route:** Only the team owner can delete tasks.

    **Errors:**
    - 403: Authenticated user is not the team owner
    - 404: Task not found
    """
    task = TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    project = _get_project_or_404(db, task.project_id)
    _require_team_owner(db, project.team_id, current_user)
    TaskService.delete_task(db, task)
