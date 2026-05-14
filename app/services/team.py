"""
Team service containing business logic for team management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate


class TeamService:
    """Service for team CRUD operations."""

    @staticmethod
    def create_team(db: Session, team_create: TeamCreate, owner_id: int) -> Team:
        """
        Create a new team owned by the given user.

        Args:
            db: Database session
            team_create: Team creation data
            owner_id: ID of the authenticated user creating the team

        Returns:
            Created Team object
        """
        db_team = Team(
            name=team_create.name,
            description=team_create.description,
            owner_id=owner_id,
        )
        db.add(db_team)
        db.commit()
        db.refresh(db_team)
        return db_team

    @staticmethod
    def get_teams_for_user(db: Session, owner_id: int) -> List[Team]:
        """
        Retrieve all teams owned by the given user.

        Args:
            db: Database session
            owner_id: ID of the authenticated user

        Returns:
            List of Team objects
        """
        return db.execute(
            select(Team).where(Team.owner_id == owner_id)
        ).scalars().all()

    @staticmethod
    def get_team_by_id(db: Session, team_id: int) -> Optional[Team]:
        """
        Retrieve a single team by its ID.

        Args:
            db: Database session
            team_id: Team's ID

        Returns:
            Team object if found, None otherwise
        """
        return db.execute(
            select(Team).where(Team.id == team_id)
        ).scalar_one_or_none()

    @staticmethod
    def update_team(db: Session, team: Team, team_update: TeamUpdate) -> Team:
        """
        Apply partial updates to a team.

        Args:
            db: Database session
            team: Existing Team object
            team_update: Fields to update (only non-None values are applied)

        Returns:
            Updated Team object
        """
        update_data = team_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(team, field, value)
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def delete_team(db: Session, team: Team) -> None:
        """
        Delete a team.

        Args:
            db: Database session
            team: Team object to delete
        """
        db.delete(team)
        db.commit()
