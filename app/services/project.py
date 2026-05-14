"""
Project service containing business logic for project management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.project import Project
from app.models.team import Team
from app.models.team_member import TeamMember
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project CRUD operations."""

    @staticmethod
    def get_user_projects(db: Session, user_id: int) -> List[Project]:
        """Retrieve all projects across all teams the user belongs to."""
        # Teams owned by user
        owned_teams_query = select(Team.id).where(Team.owner_id == user_id)
        # Teams where user is a member
        member_teams_query = select(TeamMember.team_id).where(TeamMember.user_id == user_id)
        
        # Combine team IDs
        team_ids = set(db.execute(owned_teams_query).scalars().all()) | set(db.execute(member_teams_query).scalars().all())
        
        if not team_ids:
            return []
            
        return db.execute(
            select(Project).where(Project.team_id.in_(list(team_ids)))
        ).scalars().all()

    @staticmethod
    def create_project(
        db: Session, project_create: ProjectCreate, team_id: int
    ) -> Project:
        """
        Create a new project under the given team.

        Args:
            db: Database session
            project_create: Project creation data
            team_id: ID of the team owning this project

        Returns:
            Created Project object
        """
        db_project = Project(
            team_id=team_id,
            name=project_create.name,
            description=project_create.description,
            status=project_create.status or "active",
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def get_projects_for_team(db: Session, team_id: int) -> List[Project]:
        """
        Retrieve all projects belonging to a team.

        Args:
            db: Database session
            team_id: Team's ID

        Returns:
            List of Project objects
        """
        return db.execute(
            select(Project).where(Project.team_id == team_id)
        ).scalars().all()

    @staticmethod
    def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
        """
        Retrieve a single project by its ID.

        Args:
            db: Database session
            project_id: Project's ID

        Returns:
            Project object if found, None otherwise
        """
        return db.execute(
            select(Project).where(Project.id == project_id)
        ).scalar_one_or_none()

    @staticmethod
    def update_project(
        db: Session, project: Project, project_update: ProjectUpdate
    ) -> Project:
        """
        Apply partial updates to a project.

        Args:
            db: Database session
            project: Existing Project object
            project_update: Fields to update (only non-None values are applied)

        Returns:
            Updated Project object
        """
        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project: Project) -> None:
        """
        Delete a project.

        Args:
            db: Database session
            project: Project object to delete
        """
        db.delete(project)
        db.commit()
