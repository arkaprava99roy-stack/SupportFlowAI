"""Tests for order tools, two-phase cancellations, tickets, and audit logging."""
import pytest
from src.db.seed import seed_database
from src.agent.tools.order_tools import get_order, cancel_order
from src.agent.tools.ticket_tools import create_support_ticket, get_pending_reviews
from src.agent.tools.audit_logger import get_recent_audit_logs


@pytest.fixture(autouse=True)
def setup_db():
    """Seeds database before each test run."""
    seed_database()


def test_get_order_authorized():
    """Verify customer can view their own order."""
    res = get_order("ORD-1001", user_id="user_demo")
    assert res["success"] is True
    assert res["order_id"] == "ORD-1001"
    assert res["status"] == "PROCESSING"
    assert "Noise-Cancelling" in res["product_name"]


def test_get_order_unauthorized_access_refusal():
    """Verify accessing another customer's order is blocked."""
    # ORD-1005 belongs to user_2, not user_demo
    res = get_order("ORD-1005", user_id="user_demo")
    assert res["success"] is False
    assert res["error"] == "UNAUTHORIZED"
    assert "Access Denied" in res["message"]


def test_cancel_order_requires_explicit_confirmation():
    """Non-negotiable engineering practice: cancellation must NOT execute without confirmation."""
    # First call with confirmation=False
    res1 = cancel_order("ORD-1001", confirmation=False, user_id="user_demo")
    assert res1["success"] is False
    assert res1["requires_confirmation"] is True
    assert "Confirmation Required" in res1["message"]

    # Verify order is still PROCESSING in the DB
    check = get_order("ORD-1001", user_id="user_demo")
    assert check["status"] == "PROCESSING"


def test_cancel_order_after_confirmation():
    """Verify order is cancelled and refund initiated once confirmed."""
    # Call with confirmation=True
    res2 = cancel_order("ORD-1001", confirmation=True, user_id="user_demo")
    assert res2["success"] is True
    assert res2["status"] == "CANCELLED"
    assert "Successfully Cancelled" in res2["message"]

    # Verify order is now CANCELLED in the DB
    check = get_order("ORD-1001", user_id="user_demo")
    assert check["status"] == "CANCELLED"


def test_cancel_order_ineligible_delivered():
    """Verify already DELIVERED orders cannot be cancelled."""
    # ORD-1002 is DELIVERED
    res = cancel_order("ORD-1002", confirmation=True, user_id="user_demo")
    assert res["success"] is False
    assert res["error"] == "INELIGIBLE_STATUS"


def test_create_support_ticket_and_audit_logging():
    """Verify support ticket generation and audit log persistence."""
    ticket_res = create_support_ticket(
        user_id="user_demo",
        title="Question regarding 4K monitor refresh rate",
        description="Customer wants to know if 144Hz is supported via HDMI 2.1.",
        priority="LOW",
        category="PRODUCT_INFO",
    )
    assert ticket_res["success"] is True
    assert ticket_res["ticket_id"].startswith("TICK-")

    # Verify audit logs
    audit_logs = get_recent_audit_logs(limit=5)
    assert len(audit_logs) > 0
    assert any(log["tool_name"] == "create_support_ticket" for log in audit_logs)
