from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLITE_URL = "sqlite:///./data.chores.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def get_db() -> Generator:
    """Yield a SQLAlchemy session (used as FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
