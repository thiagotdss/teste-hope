import os

os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5433/consultas"

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)