from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class TeamMember(BaseModel):
    """Association model representing a user's membership in a team.

    Inherits audit timestamps (created_at, updated_at) from BaseModel.
    """

    __tablename__ = "team_members"

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_members_team_user"),
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of the team this membership belongs to",
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of the user who is a member",
    )

    role = Column(
        String(50),
        nullable=False,
        default="member",
        doc="Role of the user within the team (e.g. member, admin)",
    )

    team = relationship(
        "Team",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="team_memberships",
    )

    def __repr__(self) -> str:
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role='{self.role}')>"
