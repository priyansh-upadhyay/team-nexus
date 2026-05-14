"""
Task service containing business logic for task management.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.task import Task
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.team import Team
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service for task CRUD operations."""

    @staticmethod
    def get_user_tasks(db: Session, user_id: int) -> List[Task]:
        """Retrieve all tasks across all projects the user has access to."""
        # Teams owned by user
        owned_teams_query = select(Team.id).where(Team.owner_id == user_id)
        # Teams where user is a member
        member_teams_query = select(TeamMember.team_id).where(TeamMember.user_id == user_id)
        
        team_ids = set(db.execute(owned_teams_query).scalars().all()) | set(db.execute(member_teams_query).scalars().all())
        
        if not team_ids:
            return []
            
        # Get all project IDs for these teams
        project_ids_query = select(Project.id).where(Project.team_id.in_(list(team_ids)))
        project_ids = db.execute(project_ids_query).scalars().all()
        
        if not project_ids:
            # Maybe the user has tasks assigned even if not part of a team? (Shouldn't happen but safe)
            return db.execute(
                select(Task).where(Task.assignee_id == user_id)
            ).scalars().all()
            
        return db.execute(
            select(Task).where(
                (Task.project_id.in_(list(project_ids))) | (Task.assignee_id == user_id)
            )
        ).scalars().all()

    @staticmethod
    def create_task(
        db: Session, task_create: TaskCreate, project_id: int, team_id: int
    ) -> Task:
        """
        Create a new task under the given project.

        Args:
            db: Database session
            task_create: Task creation data
            project_id: ID of the project owning this task
            team_id: ID of the team (used to validate assignee membership)

        Returns:
            Created Task object

        Raises:
            ValueError: If assignee is not a member of the team
        """
        if task_create.assignee_id is not None:
            TaskService._validate_assignee(db, task_create.assignee_id, team_id)

        db_task = Task(
            project_id=project_id,
            title=task_create.title,
            description=task_create.description,
            status=task_create.status or "todo",
            priority=task_create.priority or "medium",
            assignee_id=task_create.assignee_id,
            due_date=task_create.due_date,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def get_tasks_for_project(db: Session, project_id: int) -> List[Task]:
        """
        Retrieve all tasks belonging to a project.

        Args:
            db: Database session
            project_id: Project's ID

        Returns:
            List of Task objects
        """
        return db.execute(
            select(Task).where(Task.project_id == project_id)
        ).scalars().all()

    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
        """
        Retrieve a single task by its ID.

        Args:
            db: Database session
            task_id: Task's ID

        Returns:
            Task object if found, None otherwise
        """
        return db.execute(
            select(Task).where(Task.id == task_id)
        ).scalar_one_or_none()

    @staticmethod
    def update_task(
        db: Session, task: Task, task_update: TaskUpdate, team_id: int
    ) -> Task:
        """
        Apply partial updates to a task.

        Args:
            db: Database session
            task: Existing Task object
            task_update: Fields to update (only non-None values are applied)
            team_id: ID of the team (used to validate assignee membership)

        Returns:
            Updated Task object

        Raises:
            ValueError: If new assignee is not a member of the team
        """
        if task_update.assignee_id is not None:
            TaskService._validate_assignee(db, task_update.assignee_id, team_id)

        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task: Task) -> None:
        """
        Delete a task.

        Args:
            db: Database session
            task: Task object to delete
        """
        db.delete(task)
        db.commit()

    @staticmethod
    def _validate_assignee(db: Session, assignee_id: int, team_id: int) -> None:
        """
        Ensure the assignee exists and is a member of the team.

        Raises:
            ValueError: If user does not exist or is not a team member/owner
        """
        user = db.execute(
            select(User).where(User.id == assignee_id)
        ).scalar_one_or_none()

        if not user:
            raise ValueError(f"User {assignee_id} does not exist")

        # Accept team members and the team owner (owner may not have a TeamMember row)
        membership = db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == assignee_id,
            )
        ).scalar_one_or_none()

        if not membership:
            # Check if the user is the team owner via the teams table
            from app.models.team import Team  # local import avoids circular at module level
            team = db.execute(
                select(Team).where(Team.id == team_id)
            ).scalar_one_or_none()

            if not team or team.owner_id != assignee_id:
                raise ValueError(
                    f"User {assignee_id} is not a member of this team"
                )
