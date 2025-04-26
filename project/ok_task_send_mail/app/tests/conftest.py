# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.src.main import app  # パスはプロジェクト構成に合わせて修正してください

@pytest.fixture
def client():
    return TestClient(app)