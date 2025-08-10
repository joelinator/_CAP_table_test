# tests/test_api.py
# Integration test example, assuming pytest-fastapi or similar
from fastapi.testclient import TestClient
import pytest
from app.adapters.controllers.api import app
from unittest.mock import Mock, patch

client = TestClient(app)

def test_login():
    response = client.post("/api/token/", json={"username": "admin", "password": "adminpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.fixture
def mock_get_current_user():
    with patch("app.adapters.controllers.api.get_current_user") as mock:
        user = Mock(id=1, username="admin", role="ADMIN")
        mock.return_value = user
        yield mock

def test_get_shareholders_admin(mock_get_current_user):
    with patch("app.adapters.controllers.api.ListShareholders") as mock_list:
        mock_list.return_value.execute.return_value = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "total_shares": 100}
        ]
        with patch("app.adapters.controllers.api.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "admin"}
            response = client.get("/api/shareholders/", headers={"Authorization": "Bearer dummy-token"})
            assert response.status_code == 200
            assert response.json() == [
                {"id": 1, "name": "John Doe", "email": "john@example.com", "total_shares": 100}
            ]
