from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model for authentication and user management in the SaaS application.

    Uses email-only authentication architecture. Inherits audit timestamps
    (created_at, updated_at) from BaseModel.
    """

    __tablename__ = "users"

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="User's email address - used for authentication and communication"
    )

    hashed_password = Column(
        String(128),
        nullable=False,
        doc="Bcrypt-hashed password for secure authentication"
    )

    full_name = Column(
        String(100),
        nullable=False,
        doc="User's full display name"
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active and can authenticate"
    )

    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user has superuser/admin privileges across the platform"
    )

    # Future relationships (to be added when models are created):
    # memberships: relationship to Membership (user's organization memberships)
    # organizations: relationship to Organization via memberships (many-to-many)
    # assigned_tasks: relationship to Task (tasks assigned to this user)
    # created_tasks: relationship to Task (tasks created by this user)
    # invitations: relationship to Invitation (invitations sent/received by user)

    team_memberships = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    assigned_tasks = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )

    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"