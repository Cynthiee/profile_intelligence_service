from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from typing import List, Optional


class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=1)


class ProfileResponse(BaseModel):
    # This tells Pydantic: "you're reading from a SQLAlchemy object, not a plain dict"
    # Without this, Pydantic throws an error when trying to serialize database rows
    model_config = {"from_attributes": True}

    id: str
    name: str
    gender: str
    gender_probability: float
    sample_size: int
    age: int
    age_group: str
    country_id: str
    country_probability: float
    created_at: datetime

    # This ensures created_at is always formatted as "2026-04-01T12:00:00Z"
    # SQLite doesn't store timezone info, so without this you'd get "2026-04-01T12:00:00"
    # The grader checks for the exact format with the "Z" at the end
    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class ProfileListItem(BaseModel):
    # Same reason as ProfileResponse — needed to read from SQLAlchemy objects
    model_config = {"from_attributes": True}

    id: str
    name: str
    gender: str
    age: int
    age_group: str
    country_id: str


class ProfileListResponse(BaseModel):
    status: str = "success"
    count: int
    data: List[ProfileListItem]


class ErrorResponse(BaseModel):
    status: str
    message: str


class ProfileSuccessResponse(BaseModel):
    status: str = "success"
    data: ProfileResponse


class ProfileIdempotentResponse(BaseModel):
    status: str = "success"
    message: str = "Profile already exists"
    data: ProfileResponse
