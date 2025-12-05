# File: `tests/conftest.py`
import os
import sys
from pathlib import Path

import pytest

# Configure test database URL before importing the app/ORM
ROOT = Path(__file__).resolve().parents[1]
TEST_DB_PATH = ROOT / "data" / "test_db.sqlite"
TEST_DB_PATH.parent.mkdir(exist_ok=True)
os.environ.setdefault("TEST_DB_URL", f"sqlite:///{TEST_DB_PATH}")

# add repo root to sys.path before importing app
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from starlette.testclient import TestClient  # noqa: E402

from adapters.persistence import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def clean_db():
    """Recreate schema for each test to keep isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
