"""
Pydantic schemas for team membership endpoints.

Handles request/response validation and serialization.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TeamMemberAdd(BaseModel):
    """Schema for adding a user to a team."""

    user_id: int = Field(..., description="ID of the user to add to the team")
    role: Optional[str] = Field("member", description="Role of the user within the team")


class TeamMemberResponse(BaseModel):
    """Schema for returning team membership information in API responses."""

    id: int = Field(..., description="Membership record unique identifier")
    team_id: int = Field(..., description="ID of the team")
    user_id: int = Field(..., description="ID of the member user")
    user_email: Optional[str] = Field(None, description="Email of the member user")
    role: str = Field(..., description="Role of the user within the team")

    class Config:
        from_attributes = True
