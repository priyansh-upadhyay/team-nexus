from sqlalchemy import Column, String, Text, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Task(BaseModel):
    """Task model belonging to a project with kanban-ready status and priority fields.

    Inherits audit timestamps (created_at, updated_at) from BaseModel.
    """

    __tablename__ = "tasks"

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of the project this task belongs to",
    )

    title = Column(
        String(200),
        nullable=False,
        doc="Task title",
    )

    description = Column(
        Text,
        nullable=True,
        doc="Optional task description",
    )

    status = Column(
        String(50),
        nullable=False,
        default="todo",
        doc="Task status: todo | in_progress | review | done",
    )

    priority = Column(
        String(50),
        nullable=False,
        default="medium",
        doc="Task priority: low | medium | high",
    )

    assignee_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="ID of the user assigned to this task",
    )

    due_date = Column(
        Date,
        nullable=True,
        doc="Optional due date for the task",
    )

    project = relationship(
        "Project",
        back_populates="tasks",
    )

    assignee = relationship(
        "User",
        back_populates="assigned_tasks",
    )

    def __repr__(self) -> str:
        return (
            f"<Task(id={self.id}, title='{self.title}', "
            f"status='{self.status}', project_id={self.project_id})>"
        )
