"""Tests for orders API, user isolation, cancellations, and feedback."""
import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.db.seed import seed_database
from src.auth.jwt_handler import create_access_token

client = TestClient(app)


def get_demo_user_headers():
    """Generates valid JWT bearer headers for user_demo."""
    token = create_access_token(data={"sub": "user_demo", "email": "alex.demo@supportflow.ai", "role": "customer"})
    return {"Authorization": f"Bearer {token}"}


def get_user_2_headers():
    """Generates valid JWT bearer headers for user_2."""
    token = create_access_token(data={"sub": "user_2", "email": "david.chen@example.com", "role": "customer"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def setup_db():
    """Initializes and seeds database before order tests."""
    seed_database()


def test_get_user_orders_only_own_records():
    """Verify user only receives their own orders."""
    headers = get_demo_user_headers()
    res = client.get("/api/orders", headers=headers)
    assert res.status_code == 200
    orders = res.json()
    assert len(orders) >= 2
    order_ids = [o["id"] for o in orders]
    assert "ORD-1001" in order_ids
    assert "ORD-1002" in order_ids
    # Ensure other users' orders are NOT present
    assert "ORD-1005" not in order_ids


def test_get_order_by_id_forbidden_for_other_user():
    """Verify user cannot view another customer's order by ID."""
    headers = get_demo_user_headers()
    # ORD-1005 belongs to user_2
    res = client.get("/api/orders/ORD-1005", headers=headers)
    assert res.status_code == 403
    assert "Access Denied" in res.json()["detail"]


def test_cancel_order_two_phase_confirmation_api():
    """Verify cancellation requires confirmation and initiates refund on confirmation."""
    headers = get_demo_user_headers()

    # Step 1: Confirmation required
    res1 = client.post("/api/orders/ORD-1001/cancel", json={"confirmation": False}, headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["requires_confirmation"] is True
    assert "Confirmation Required" in data1["message"]

    # Step 2: Confirm cancellation
    res2 = client.post("/api/orders/ORD-1001/cancel", json={"confirmation": True}, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["success"] is True
    assert data2["status"] == "CANCELLED"
    assert "$299.99" in data2["refund_amount"]


def test_submit_feedback_endpoint():
    """Verify thumbs up feedback submission and summary statistics."""
    headers = get_demo_user_headers()

    # Start a chat to get conversation_id
    chat_res = client.post("/api/chat", json={"message": "What payment options do you accept?"}, headers=headers)
    conv_id = chat_res.json()["conversation_id"]

    # Submit feedback
    fb_payload = {
        "conversation_id": conv_id,
        "rating": "thumbs_up",
        "comment": "Very clear and helpful response!",
    }
    fb_res = client.post("/api/feedback", json=fb_payload, headers=headers)
    assert fb_res.status_code == 201
    assert fb_res.json()["success"] is True

    # Check feedback summary
    sum_res = client.get("/api/feedback/summary", headers=headers)
    assert sum_res.status_code == 200
    summary = sum_res.json()
    assert summary["total_feedback"] >= 1
    assert summary["thumbs_up"] >= 1
