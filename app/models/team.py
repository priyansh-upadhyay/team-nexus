from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Team(BaseModel):
    """Team model for grouping users in the SaaS application.

    Inherits audit timestamps (created_at, updated_at) from BaseModel.
    """

    __tablename__ = "teams"

    name = Column(
        String(100),
        nullable=False,
        doc="Team display name",
    )

    description = Column(
        Text,
        nullable=True,
        doc="Optional team description",
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of the user who owns this team",
    )

    owner = relationship(
        "User",
        backref="owned_teams",
        lazy="joined",
    )

    members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
    )

    projects = relationship(
        "Project",
        back_populates="team",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
