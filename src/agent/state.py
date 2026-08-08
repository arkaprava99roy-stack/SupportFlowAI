"""Agent state definition for SupportFlow AI LangGraph workflow (Phase 1 & Phase 2)."""
from typing import Annotated, Sequence, Optional, List, Dict, Any, Literal
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# Valid intent classifications
IntentType = Literal[
    "BILLING",
    "REFUND",
    "TECHNICAL_SUPPORT",
    "ACCOUNT",
    "PRODUCT_INFO",
    "SHIPPING",
    "SECURITY",
    "GENERAL",
]

# Valid risk severity levels
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


class AgentState(TypedDict):
    """The unified state passed through the LangGraph support workflow."""

    # User & Context
    user_id: Optional[str]
    conversation_id: Optional[str]

    # Core conversation history with append reducer
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Safety Guardrails
    is_safe: bool
    guardrail_violation: Optional[str]

    # Intent classification
    intent: Optional[IntentType]
    intent_confidence: Optional[float]

    # Risk analysis & security scoring
    risk_level: Optional[RiskLevel]
    risk_score: Optional[float]
    risk_reason: Optional[str]

    # Tool invocation & execution
    tool_calls: Optional[List[Dict[str, Any]]]
    tool_results: Optional[List[Dict[str, Any]]]
    pending_confirmation: Optional[Dict[str, Any]]

    # RAG knowledge retrieval and citations
    retrieved_docs: Optional[List[Dict[str, Any]]]
    citations: Optional[List[Dict[str, Any]]]

    # Escalation & Ticket status
    is_escalated: bool
    escalation_reason: Optional[str]
    ticket_id: Optional[str]
    review_id: Optional[str]

    # Final generated response text
    response_text: Optional[str]
