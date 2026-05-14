"""
Pydantic schemas for task endpoints.

Handles request/response validation and serialization.
"""

from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field

TaskStatus = Literal["todo", "in_progress", "review", "done"]
TaskPriority = Literal["low", "medium", "high"]


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Optional task description")
    status: Optional[TaskStatus] = Field("todo", description="Task status")
    priority: Optional[TaskPriority] = Field("medium", description="Task priority")
    assignee_id: Optional[int] = Field(None, description="ID of the user to assign")
    due_date: Optional[date] = Field(None, description="Optional due date (YYYY-MM-DD)")
    project_id: int = Field(..., description="ID of the project this task belongs to")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Optional task description")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    assignee_id: Optional[int] = Field(None, description="ID of the user to assign")
    due_date: Optional[date] = Field(None, description="Optional due date (YYYY-MM-DD)")


class TaskResponse(BaseModel):
    """Schema for returning task information in API responses."""

    id: int = Field(..., description="Task's unique identifier")
    project_id: int = Field(..., description="ID of the project this task belongs to")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field(..., description="Task status")
    priority: str = Field(..., description="Task priority")
    assignee_id: Optional[int] = Field(None, description="ID of the assigned user")
    due_date: Optional[date] = Field(None, description="Task due date")

    class Config:
        from_attributes = True
