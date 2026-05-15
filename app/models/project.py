from typing import Optional
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Project(BaseModel):
    """Project model belonging to a team.

    Inherits audit timestamps (created_at, updated_at) from BaseModel.
    """

    __tablename__ = "projects"

    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of the team this project belongs to",
    )

    name = Column(
        String(100),
        nullable=False,
        doc="Project display name",
    )

    description = Column(
        Text,
        nullable=True,
        doc="Optional project description",
    )

    status = Column(
        String(50),
        nullable=False,
        default="active",
        doc="Current project status (e.g. active, archived)",
    )

    progress = Column(
        Integer,
        nullable=False,
        default=0,
        doc="Project progress percentage (0-100)",
    )

    start_date = Column(
        String(50),
        nullable=True,
        doc="Project start date",
    )

    due_date = Column(
        String(50),
        nullable=True,
        doc="Project due date",
    )

    team = relationship(
        "Team",
        back_populates="projects",
    )

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    @property
    def team_name(self) -> Optional[str]:
        """Return the name of the owning team."""
        return self.team.name if self.team else None

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', team_id={self.team_id})>"
