# File: `tests/conftest.py`
import sys
from pathlib import Path

import pytest

# add repo root to sys.path before importing app
ROOT = Path(__file__).resolve().parents[1]  # repository root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from starlette.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
