from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=1)

class ProfileResponse(BaseModel):
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

class ProfileListItem(BaseModel):
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