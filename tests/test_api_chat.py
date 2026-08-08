"""Tests for chat endpoint, conversation persistence, citations, and escalation."""
import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.db.seed import seed_database

client = TestClient(app)


def get_authenticated_headers():
    """Helper creating a test user and returning Bearer auth headers."""
    email = "chat_test_user@example.com"
    pwd = "ChatPassword789!"
    reg_payload = {"email": email, "password": pwd, "name": "Chat Test User"}
    reg_res = client.post("/api/auth/register", json=reg_payload)
    if reg_res.status_code == 201:
        token = reg_res.json()["access_token"]
    else:
        login_res = client.post("/api/auth/login", json={"email": email, "password": pwd})
        token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def setup_db():
    """Initializes and seeds database before chat tests."""
    seed_database()


def test_api_chat_standard_rag_query():
    """Verify POST /api/chat returns grounded response with citations."""
    headers = get_authenticated_headers()
    payload = {
        "message": "What is the return window and refund policy for items?",
    }
    res = client.post("/api/chat", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "conversation_id" in data
    assert data["intent"] == "REFUND"
    assert data["is_escalated"] is False
    assert len(data["response"]) > 20
    assert len(data["citations"]) > 0

    # Verify conversation summary in GET /api/conversations
    conv_res = client.get("/api/conversations", headers=headers)
    assert conv_res.status_code == 200
    conv_list = conv_res.json()
    assert len(conv_list) >= 1
    assert conv_list[0]["id"] == data["conversation_id"]


def test_api_chat_multi_turn_history_persistence():
    """Verify conversation history persists across multiple turns."""
    headers = get_authenticated_headers()

    # Turn 1
    t1_res = client.post("/api/chat", json={"message": "Hello, I have a support question."}, headers=headers)
    assert t1_res.status_code == 200
    conv_id = t1_res.json()["conversation_id"]

    # Turn 2 in same conversation
    t2_res = client.post("/api/chat", json={"message": "Can you explain the shipping times?", "conversation_id": conv_id}, headers=headers)
    assert t2_res.status_code == 200

    # Fetch complete conversation history via GET /api/conversations/{id}
    detail_res = client.get(f"/api/conversations/{conv_id}", headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == conv_id
    # 2 user messages + 2 assistant messages = 4 total
    assert len(detail["messages"]) == 4
    assert detail["messages"][0]["sender"] == "user"
    assert detail["messages"][1]["sender"] == "assistant"


def test_api_chat_high_risk_escalation_ticket():
    """Verify high-risk security query generates support ticket and escalation flags."""
    headers = get_authenticated_headers()
    payload = {
        "message": "Someone compromised my account and logged in from an unknown location!",
    }
    res = client.post("/api/chat", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "SECURITY"
    assert data["risk_level"] == "HIGH"
    assert data["is_escalated"] is True
    assert data["ticket_id"] is not None
    assert data["ticket_id"].startswith("TICK-")
