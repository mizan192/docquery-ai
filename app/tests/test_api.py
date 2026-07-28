import pytest
from fastapi.testclient import TestClient
from app.main import app


# create test client fixture
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    """root endpoint should return app info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert data["app"] == "DocSense AI"


def test_health_endpoint_returns_200(client):
    """health endpoint should return 200"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_upload_requires_authentication(client):
    """upload endpoint should reject unauthenticated requests"""
    response = client.post("/api/v1/documents/upload")
    assert response.status_code == 401


def test_chat_requires_authentication(client):
    """chat endpoint should reject unauthenticated requests"""
    response = client.post(
        "/api/v1/chat",
        json={"question": "test question"}
    )
    assert response.status_code == 401


def test_search_requires_authentication(client):
    """search endpoint should reject unauthenticated requests"""
    response = client.post(
        "/api/v1/search",
        json={"question": "test question"}
    )
    assert response.status_code == 401


def test_register_missing_fields(client):
    """register should fail with missing fields"""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@test.com"}
        # missing username and password!
    )
    assert response.status_code == 422


def test_login_wrong_credentials(client):
    """login should fail with wrong credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@test.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_chat_history_requires_auth(client):
    """chat history should require authentication"""
    response = client.get("/api/v1/chat/history")
    assert response.status_code == 401
    