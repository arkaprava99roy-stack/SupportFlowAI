"""Tool execution node: handles order lookups, safe cancellations, and ticket creation."""
import re
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage

from src.agent.state import AgentState
from src.agent.nodes.intent_classifier import get_latest_user_message
from src.agent.tools.order_tools import get_order, cancel_order, normalize_order_id
from src.agent.tools.ticket_tools import create_support_ticket
from src.utils.logger import logger


def extract_order_id(text: str) -> Optional[str]:
    """Extracts order identifier patterns such as ORD-1001, #1001, or order 1001."""
    # Pattern like ORD-1001
    match = re.search(r"\b(ORD-\d{3,6})\b", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    # Pattern like #1001 or order 1001
    match = re.search(r"(?:order|ord|#)\s*#?\s*(\d{3,6})\b", text, re.IGNORECASE)
    if match:
        return f"ORD-{match.group(1)}"

    return None


def is_cancellation_intent(text: str) -> bool:
    """Checks if message expresses order cancellation request."""
    patterns = [r"\bcancel\b", r"\bcancelling\b", r"\bcancellation\b", r"\bstop\s+my\s+order\b"]
    return any(re.search(p, text.lower()) for p in patterns)


def is_confirmation_response(text: str) -> bool:
    """Checks if the user explicitly confirms a pending sensitive action."""
    patterns = [
        r"\byes\b",
        r"\bconfirm\b",
        r"\bi\s+confirm\b",
        r"\bproceed\b",
        r"\bgo\s+ahead\b",
        r"\bconfirm\s+cancel\b",
        r"\bplease\s+cancel\b",
        r"\bconfirm\s+cancellation\b",
        r"\byep\b",
        r"\bsure\b",
    ]
    return any(re.search(p, text.lower()) for p in patterns)


def tool_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node: executes tools when specific order or ticket actions are requested."""
    user_message = get_latest_user_message(state.get("messages", []))
    user_id = state.get("user_id", "user_demo") or "user_demo"
    order_id = extract_order_id(user_message)

    # Check if there is an existing pending confirmation from previous turn
    pending_conf = state.get("pending_confirmation")
    if pending_conf and not order_id:
        order_id = pending_conf.get("order_id")

    tool_calls: List[Dict[str, Any]] = []
    tool_results: List[Dict[str, Any]] = []

    # 1. Cancellation Flow
    if is_cancellation_intent(user_message) or (pending_conf and is_confirmation_response(user_message)):
        if order_id:
            confirmed = is_confirmation_response(user_message)
            tool_calls.append({"tool": "cancel_order", "args": {"order_id": order_id, "confirmation": confirmed}})

            result = cancel_order(
                order_id=order_id,
                confirmation=confirmed,
                reason="Customer requested via chat",
                user_id=user_id,
            )
            tool_results.append(result)

            if result.get("requires_confirmation"):
                return {
                    "tool_calls": tool_calls,
                    "tool_results": tool_results,
                    "pending_confirmation": {"order_id": order_id, "action": "cancel_order"},
                }
            else:
                return {
                    "tool_calls": tool_calls,
                    "tool_results": tool_results,
                    "pending_confirmation": None,
                }

    # 2. Order Lookup Flow
    if order_id and ("status" in user_message.lower() or "where" in user_message.lower() or "track" in user_message.lower() or "order" in user_message.lower() or "details" in user_message.lower()):
        tool_calls.append({"tool": "get_order", "args": {"order_id": order_id, "user_id": user_id}})
        result = get_order(order_id=order_id, user_id=user_id)
        tool_results.append(result)
        return {
            "tool_calls": tool_calls,
            "tool_results": tool_results,
        }

    return {
        "tool_calls": [],
        "tool_results": [],
    }
