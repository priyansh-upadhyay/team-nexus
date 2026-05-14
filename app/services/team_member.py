"""
Team membership service containing business logic for member management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.user import User
from app.schemas.team_member import TeamMemberAdd


class TeamMemberService:
    """Service for team membership operations."""

    @staticmethod
    def add_member_to_team(
        db: Session,
        team: Team,
        member_add: TeamMemberAdd,
    ) -> TeamMember:
        """
        Add a user to a team.

        Args:
            db: Database session
            team: Validated Team object
            member_add: Membership creation data

        Returns:
            Created TeamMember object

        Raises:
            ValueError: If user does not exist or is already a member
        """
        user = db.execute(
            select(User).where(User.id == member_add.user_id)
        ).scalar_one_or_none()

        if not user:
            raise ValueError(f"User {member_add.user_id} does not exist")

        existing = db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == member_add.user_id,
            )
        ).scalar_one_or_none()

        if existing:
            raise ValueError(f"User {member_add.user_id} is already a member of this team")

        db_member = TeamMember(
            team_id=team.id,
            user_id=member_add.user_id,
            role=member_add.role or "member",
        )
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def get_team_members(db: Session, team_id: int) -> List[TeamMember]:
        """
        Retrieve all members of a team.

        Args:
            db: Database session
            team_id: Team's ID

        Returns:
            List of TeamMember objects
        """
        return db.execute(
            select(TeamMember).where(TeamMember.team_id == team_id)
        ).scalars().all()

    @staticmethod
    def get_membership(
        db: Session, team_id: int, user_id: int
    ) -> Optional[TeamMember]:
        """
        Retrieve a specific membership record.

        Args:
            db: Database session
            team_id: Team's ID
            user_id: User's ID

        Returns:
            TeamMember object if found, None otherwise
        """
        return db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        ).scalar_one_or_none()

    @staticmethod
    def remove_member_from_team(db: Session, membership: TeamMember) -> None:
        """
        Remove a user from a team.

        Args:
            db: Database session
            membership: TeamMember object to delete
        """
        db.delete(membership)
        db.commit()
