from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Optional

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

app = FastAPI(title="Profile Intelligence Service")

# CORS (required by grading script)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.post("/api/profiles", status_code=201)
async def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    if not profile.name or not profile.name.strip():
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(status="error", message="Missing or empty name").model_dump()
        )

    name_clean = profile.name.strip()

    # Idempotency check
    existing = db.query(Profile).filter(Profile.name == name_clean).first()
    if existing:
        return ProfileIdempotentResponse(data=existing)

    try:
        data = await fetch_profile_data(name_clean)
    except ValueError as e:
        api_name = str(e).split()[0]
        raise HTTPException(
            status_code=502,
            detail={"status": "502", "message": f"{api_name} returned an invalid response"}
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
            detail=ErrorResponse(status="error", message="Profile not found").model_dump()
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
            detail=ErrorResponse(status="error", message="Profile not found").model_dump()
        )
    db.delete(profile)
    db.commit()
    return None
