from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.dialects.sqlite import CHAR
from datetime import datetime, timezone
import uuid
from uuid6 import uuid7

from .database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid7()))
    name = Column(String, unique=True, nullable=False, index=True)
    gender = Column(String, nullable=False)
    gender_probability = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String, nullable=False)
    country_id = Column(String, nullable=False)
    country_probability = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

