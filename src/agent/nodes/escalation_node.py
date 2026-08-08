"""Escalation node: handles HIGH risk queries, generates support tickets, and enqueues human review."""
from typing import Dict, Any
from langchain_core.messages import AIMessage

from src.agent.state import AgentState
from src.agent.nodes.intent_classifier import get_latest_user_message
from src.agent.tools.ticket_tools import create_support_ticket, enqueue_pending_review
from src.utils.logger import logger


def escalation_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node: handles immediate human handoff, creates a DB ticket, and adds to review queue."""
    user_message = get_latest_user_message(state.get("messages", []))
    user_id = state.get("user_id", "user_demo") or "user_demo"
    conversation_id = state.get("conversation_id", "session_direct") or "session_direct"
    intent = state.get("intent", "SECURITY") or "SECURITY"
    risk_reason = state.get("risk_reason", "High-severity safety/security condition detected.")

    logger.warning(f"[HIGH RISK DETECTED] Auto-creating ticket for '{user_id}': {risk_reason}")

    # 1. Create a formal support ticket in the database
    ticket_res = create_support_ticket(
        user_id=user_id,
        title=f"High Risk Alert: {risk_reason[:80]}",
        description=user_message,
        priority="HIGH",
        category=intent,
        conversation_id=conversation_id,
    )
    ticket_id = ticket_res.get("ticket_id", "TICK-EMERGENCY")

    # 2. Enqueue in the human-in-the-loop pending reviews queue
    review_id = enqueue_pending_review(
        user_id=user_id,
        conversation_id=conversation_id,
        intent=intent,
        risk_level="HIGH",
        user_message=user_message,
        ai_recommended_action="Emergency account review: verify unauthorized access, reset auth credentials, initiate owner verification.",
        ticket_id=ticket_id,
    )

    escalation_message = (
        "🚨 **High-Priority Security & Incident Escalation**\n\n"
        "We have detected a critical issue regarding **account security or potential unauthorized access**.\n\n"
        "**Actions Taken Immediately:**\n"
        f"1. **Emergency Ticket Created**: Ticket **`{ticket_id}`** has been generated and dispatched to our Senior Incident Response Team.\n"
        f"2. **Human Review Queue**: Incident assigned to supervisor review queue (`{review_id}`).\n"
        "3. **Account Safety**: We recommend navigating to **Settings > Security** to terminate other active sessions and reset your password.\n"
        "4. **Human Specialist Assigned**: A Senior Security Specialist has been alerted and will review this incident within **15 minutes**.\n\n"
        f"**Incident Reference**: `{risk_reason}`\n\n"
        "If you are locked out of your registered email address, please contact our hotline directly at `security@supportflow.ai`."
    )

    return {
        "messages": [AIMessage(content=escalation_message)],
        "response_text": escalation_message,
        "is_escalated": True,
        "escalation_reason": risk_reason,
        "ticket_id": ticket_id,
        "review_id": review_id,
        "tool_calls": [
            {
                "tool": "create_support_ticket",
                "args": {"user_id": user_id, "priority": "HIGH", "ticket_id": ticket_id},
            }
        ],
    }
