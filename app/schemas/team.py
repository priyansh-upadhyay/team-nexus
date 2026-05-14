"""
Pydantic schemas for team endpoints.

Handles request/response validation and serialization.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    """Schema for creating a new team."""

    name: str = Field(..., min_length=1, max_length=100, description="Team name")
    description: Optional[str] = Field(None, description="Optional team description")


class TeamUpdate(BaseModel):
    """Schema for updating an existing team."""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Team name")
    description: Optional[str] = Field(None, description="Optional team description")


class TeamResponse(BaseModel):
    """Schema for returning team information in API responses."""

    id: int = Field(..., description="Team's unique identifier")
    name: str = Field(..., description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    owner_id: int = Field(..., description="ID of the team owner")

    class Config:
        from_attributes = True
