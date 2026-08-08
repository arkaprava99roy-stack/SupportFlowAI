"""Guardrail node: intercepts prompt injection, jailbreaks, and unauthorized data access."""
from typing import Dict, Any
from langchain_core.messages import AIMessage

from src.agent.state import AgentState
from src.agent.nodes.intent_classifier import get_latest_user_message
from src.agent.guardrails.security_guard import evaluate_input_guardrail
from src.utils.logger import logger


def guardrail_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node: runs safety filters before intent classification and tool execution."""
    user_message = get_latest_user_message(state.get("messages", []))
    user_id = state.get("user_id", "user_demo") or "user_demo"

    verdict = evaluate_input_guardrail(user_message, current_user_id=user_id)

    if not verdict.is_safe:
        logger.warning(f"[GUARDRAIL BLOCKED] {verdict.violation_type} ({verdict.reason})")
        return {
            "is_safe": False,
            "guardrail_violation": verdict.violation_type,
            "response_text": verdict.refusal_message,
            "messages": [AIMessage(content=verdict.refusal_message or "Request blocked by security guardrails.")],
            "is_escalated": False,
        }

    return {
        "is_safe": True,
        "guardrail_violation": None,
    }
