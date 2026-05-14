"""
Team membership API endpoints.

All routes are protected and require a valid JWT token.
Add/remove operations are restricted to the team owner.
Viewing members is allowed for any team member.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.team_member import TeamMemberAdd, TeamMemberResponse
from app.services.team import TeamService
from app.services.team_member import TeamMemberService
from app.api.dependencies import get_current_active_user

router = APIRouter(
    prefix="/teams",
    tags=["Team Members"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a member to a team",
    responses={
        201: {"description": "Member added successfully"},
        400: {"description": "User already a member or does not exist"},
        403: {"description": "Not the team owner"},
        404: {"description": "Team not found"},
    },
)
async def add_member(
    team_id: int,
    member_add: TeamMemberAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TeamMemberResponse:
    """
    Add a user to a team.

    **Protected Route:** Only the team owner can add members.

    **Parameters:**
    - **user_id**: ID of the user to add
    - **role**: Role within the team (default: member)

    **Errors:**
    - 400: User does not exist or is already a member
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

    try:
        return TeamMemberService.add_member_to_team(db, team, member_add)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{team_id}/members",
    response_model=List[TeamMemberResponse],
    summary="List all members of a team",
    responses={
        200: {"description": "Members retrieved successfully"},
        403: {"description": "Not a member of this team"},
        404: {"description": "Team not found"},
    },
)
async def list_members(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[TeamMemberResponse]:
    """
    Retrieve all members of a team.

    **Protected Route:** Only team members (including the owner) can view the member list.

    **Errors:**
    - 403: Authenticated user is not a member or owner of this team
    - 404: Team not found
    """
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

    members = TeamMemberService.get_team_members(db, team_id)
    
    # Create a list of response objects with user_email populated
    response_members = []
    for m in members:
        # Pydantic will handle the conversion if we provide a dict or the object
        # But we need to ensure user_email is there
        m_dict = {
            "id": m.id,
            "team_id": m.team_id,
            "user_id": m.user_id,
            "user_email": m.user.email,
            "role": m.role
        }
        response_members.append(m_dict)
    
    # Create a dummy membership for the owner
    owner_member = {
        "id": -team.owner_id, # Dummy negative ID
        "team_id": team_id,
        "user_id": team.owner_id,
        "user_email": team.owner.email,
        "role": "owner"
    }
    
    # Check if owner is already in members (just in case)
    if not any(m["user_id"] == team.owner_id for m in response_members):
        return [owner_member] + response_members

    return response_members


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member from a team",
    responses={
        204: {"description": "Member removed successfully"},
        403: {"description": "Not the team owner"},
        404: {"description": "Team or membership not found"},
    },
)
async def remove_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Remove a user from a team.

    **Protected Route:** Only the team owner can remove members.

    **Errors:**
    - 403: Authenticated user is not the team owner
    - 404: Team not found or user is not a member
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

    membership = TeamMemberService.get_membership(db, team_id, user_id)

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found",
        )

    TeamMemberService.remove_member_from_team(db, membership)
