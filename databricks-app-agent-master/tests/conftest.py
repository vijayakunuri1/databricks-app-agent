import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app import app
from core.dependencies import get_workspace_client


@pytest.fixture
def mock_workspace_client():
    return MagicMock()


@pytest.fixture
def test_client(mock_workspace_client):
    app.dependency_overrides[get_workspace_client] = lambda: mock_workspace_client
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
