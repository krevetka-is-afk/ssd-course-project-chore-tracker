import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use DATABASE_URL env var if present (e.g. for Postgres in compose/CI).
# Fallback to SQLite file used by the project.
DEFAULT_SQLITE_URL = os.getenv("DEFAULT_SQLITE_URL", "sqlite:///./data/chores_tracker.db")
# allow overriding in tests while keeping a sensible local default
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("TEST_DB_URL") or DEFAULT_SQLITE_URL

# If using SQLite we need check_same_thread; for other DBs it's not required and should be omitted
connect_args = (
    {"check_same_thread": False} if DATABASE_URL and DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def get_db() -> Generator:
    """Yield a SQLAlchemy session (used as FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
