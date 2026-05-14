"""
Teams API endpoints.

All routes are protected and require a valid JWT token.
Update and delete operations are restricted to the team owner.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.services.team import TeamService
from app.api.dependencies import get_current_active_user

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
    responses={
        201: {"description": "Team created successfully"},
    },
)
async def create_team(
    team_create: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TeamResponse:
    """
    Create a new team owned by the authenticated user.

    **Parameters:**
    - **name**: Team name (required, max 100 characters)
    - **description**: Optional team description

    **Returns:**
    - Created team object
    """
    return TeamService.create_team(db, team_create, owner_id=current_user.id)


@router.get(
    "/",
    response_model=List[TeamResponse],
    summary="List teams owned by the current user",
    responses={
        200: {"description": "Teams retrieved successfully"},
    },
)
async def list_teams(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[TeamResponse]:
    """
    Retrieve all teams owned by the authenticated user.

    **Returns:**
    - List of team objects
    """
    return TeamService.get_teams_for_user(db, owner_id=current_user.id)


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get a team by ID",
    responses={
        200: {"description": "Team retrieved successfully"},
        403: {"description": "Not the team owner"},
        404: {"description": "Team not found"},
    },
)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TeamResponse:
    """
    Retrieve a specific team by ID.

    **Protected Route:** Only the team owner can access this endpoint.

    **Errors:**
    - 403: Authenticated user is not the team owner
    - 404: Team not found
    """
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


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Update a team",
    responses={
        200: {"description": "Team updated successfully"},
        403: {"description": "Not the team owner"},
        404: {"description": "Team not found"},
    },
)
async def update_team(
    team_id: int,
    team_update: TeamUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TeamResponse:
    """
    Update a team's name or description.

    **Protected Route:** Only the team owner can update this team.

    **Parameters:**
    - **name**: New team name (optional)
    - **description**: New team description (optional)

    **Errors:**
    - 403: Authenticated user is not the team owner
    - 404: Team not found
    """
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

    return TeamService.update_team(db, team, team_update)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a team",
    responses={
        204: {"description": "Team deleted successfully"},
        403: {"description": "Not the team owner"},
        404: {"description": "Team not found"},
    },
)
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a team permanently.

    **Protected Route:** Only the team owner can delete this team.

    **Errors:**
    - 403: Authenticated user is not the team owner
    - 404: Team not found
    """
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

    TeamService.delete_team(db, team)
