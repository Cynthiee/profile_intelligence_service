from sqlalchemy import Column, String, Float, Integer, DateTime
from datetime import datetime, timezone
from uuid6 import uuid7

from .database import Base


class Profile(Base):
    __tablename__ = "profiles"

    # UUID v7 is generated automatically for every new row
    # lambda: str(uuid7()) means "call uuid7() fresh each time" — not once at import time
    # Using generic String(36) instead of SQLite-specific CHAR so it works on PostgreSQL too
    id = Column(String(36), primary_key=True, default=lambda: str(uuid7()))

    # unique=True means the database will reject two rows with the same name
    # index=True makes lookups by name faster (used in idempotency check)
    name = Column(String, unique=True, nullable=False, index=True)

    gender = Column(String, nullable=False)
    gender_probability = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String, nullable=False)
    country_id = Column(String, nullable=False)
    country_probability = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
