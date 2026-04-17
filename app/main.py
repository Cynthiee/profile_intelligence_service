from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Optional
from app.database import engine, Base

from .database import engine, Base, get_db
from .models import Profile
from .schemas import (
    ProfileCreate,
    ProfileResponse,
    ProfileListResponse,
    ProfileListItem,
    ErrorResponse,
    ProfileSuccessResponse,
    ProfileIdempotentResponse,
)
from .services import fetch_profile_data

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Profile Intelligence Service")

# CORS — required by the grading script so it can reach your server from a browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creates all database tables on startup if they don't already exist
Base.metadata.create_all(bind=engine)


# Custom 422 handler — FastAPI's default 422 response does not match the required format
# { "status": "error", "message": "..." }
# This fires when the request body has wrong types e.g. {"name": 123}
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Invalid type"}
    )


@app.post("/api/profiles", status_code=201)
async def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    # Extra guard: Pydantic already rejects empty strings via min_length=1,
    # but this catches names that are just whitespace e.g. {"name": "   "}
    if not profile.name or not profile.name.strip():
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Missing or empty name"}
        )

    name_clean = profile.name.strip()

    # Idempotency check — if this name was already stored, return the existing record
    # This means calling POST with the same name twice won't create two entries
    existing = db.query(Profile).filter(Profile.name == name_clean).first()
    if existing:
        return ProfileIdempotentResponse(data=existing)

    # Call the three external APIs and aggregate the results
    try:
        data = await fetch_profile_data(name_clean)
    except ValueError as e:
        # str(e) is already the full message e.g. "Genderize returned an invalid response"
        # status must be "error" — not "502"
        raise HTTPException(
            status_code=502,
            detail={"status": "error", "message": str(e)}
        )

    new_profile = Profile(**data, created_at=datetime.now(timezone.utc))
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return ProfileSuccessResponse(data=new_profile)


@app.get("/api/profiles/{profile_id}")
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )
    return ProfileSuccessResponse(data=profile)


@app.get("/api/profiles", response_model=ProfileListResponse)
def list_profiles(
    gender: Optional[str] = Query(None),
    country_id: Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Profile)

    # func.lower() applies lowercase at the database level so the comparison is case-insensitive
    # e.g. gender=Male and gender=male both work
    if gender:
        query = query.filter(func.lower(Profile.gender) == gender.lower())
    if country_id:
        query = query.filter(func.lower(Profile.country_id) == country_id.lower())
    if age_group:
        query = query.filter(func.lower(Profile.age_group) == age_group.lower())

    profiles = query.all()
    data = [
        ProfileListItem(
            id=p.id,
            name=p.name,
            gender=p.gender,
            age=p.age,
            age_group=p.age_group,
            country_id=p.country_id
        ) for p in profiles
    ]
    return ProfileListResponse(count=len(data), data=data)


@app.delete("/api/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )
    db.delete(profile)
    db.commit()
    return None
