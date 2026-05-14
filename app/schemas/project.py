"""
Pydantic schemas for project endpoints.

Handles request/response validation and serialization.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, description="Optional project description")
    status: Optional[str] = Field("active", description="Project status (default: active)")
    progress: Optional[int] = Field(0, ge=0, le=100, description="Project progress (0-100)")
    start_date: Optional[date] = Field(None, description="Project start date (YYYY-MM-DD)")
    due_date: Optional[date] = Field(None, description="Project due date (YYYY-MM-DD)")
    team_id: int = Field(..., description="ID of the team this project belongs to")


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, description="Optional project description")
    status: Optional[str] = Field(None, description="Project status")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Project progress (0-100)")
    start_date: Optional[date] = Field(None, description="Project start date (YYYY-MM-DD)")
    due_date: Optional[date] = Field(None, description="Project due date (YYYY-MM-DD)")


class ProjectResponse(BaseModel):
    """Schema for returning project information in API responses."""

    id: int = Field(..., description="Project's unique identifier")
    team_id: int = Field(..., description="ID of the team this project belongs to")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: str = Field(..., description="Project status")
    progress: int = Field(..., description="Project progress (0-100)")
    start_date: Optional[date] = Field(None, description="Project start date")
    due_date: Optional[date] = Field(None, description="Project due date")
    team_name: Optional[str] = Field(None, description="Name of the team this project belongs to")

    class Config:
        from_attributes = True
