"""Tests for registration, login, JWT token issuance, and protected profile."""
import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.db.seed import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Initializes and seeds database before auth tests."""
    seed_database()


def test_register_new_user():
    """Verify new user registration issues JWT access token."""
    payload = {
        "email": "brand_new_user@example.com",
        "password": "SecurePassword123!",
        "name": "Brand New User",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == "brand_new_user@example.com"
    assert data["name"] == "Brand New User"


def test_register_duplicate_email_rejected():
    """Verify registering an existing email returns 400 Bad Request."""
    payload = {
        "email": "sarah.miller@example.com",  # Already in seed
        "password": "Password123!",
        "name": "Sarah Miller",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_existing_user():
    """Verify login with valid credentials returns JWT token."""
    # First register user
    reg_payload = {
        "email": "test_login_user@example.com",
        "password": "MySecretPassword456!",
        "name": "Test Login User",
    }
    client.post("/api/auth/register", json=reg_payload)

    # Now login
    login_payload = {
        "email": "test_login_user@example.com",
        "password": "MySecretPassword456!",
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data

    # Test protected /me endpoint with token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    profile = me_res.json()
    assert profile["email"] == "test_login_user@example.com"
    assert profile["name"] == "Test Login User"


def test_protected_route_without_token_unauthorized():
    """Verify accessing protected routes without token returns 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
