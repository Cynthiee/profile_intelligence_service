from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./profiles.db")

# check_same_thread is a SQLite-only argument — passing it to PostgreSQL causes a crash
# So we only include it when the database is SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# This is a "dependency" — FastAPI calls it before each route that needs a DB session
# yield hands the session to the route, then the finally block closes it afterwards
# This ensures the connection is always properly closed, even if an error occurs
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
