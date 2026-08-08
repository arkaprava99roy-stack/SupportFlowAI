"""LangGraph workflow definition and state graph compilation for SupportFlow AI (Phase 2)."""
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.base import BaseCheckpointSaver

from src.agent.state import AgentState
from src.agent.nodes.guardrail_node import guardrail_node
from src.agent.nodes.intent_classifier import intent_classifier_node
from src.agent.nodes.risk_analyzer import risk_analyzer_node
from src.agent.nodes.tool_node import tool_node
from src.agent.nodes.rag_node import rag_node
from src.agent.nodes.response_generator import response_generator_node
from src.agent.nodes.escalation_node import escalation_node
from src.memory.memory_manager import get_checkpointer
from src.utils.logger import logger


def route_guardrail(state: AgentState) -> Literal["intent_classifier", "__end__"]:
    """Routes based on guardrail safety verdict."""
    if not state.get("is_safe", True):
        logger.warning(f"Routing -> END (Guardrail Blocked: {state.get('guardrail_violation')})")
        return "__end__"
    return "intent_classifier"


def route_by_risk(state: AgentState) -> Literal["escalation_node", "tool_node"]:
    """Conditional router based on assessed risk level."""
    risk_level = state.get("risk_level", "LOW")
    if risk_level == "HIGH":
        logger.info("Routing -> ESCALATION_NODE (High Risk Emergency)")
        return "escalation_node"
    logger.info(f"Routing -> TOOL_NODE ({risk_level} Risk Standard Flow)")
    return "tool_node"


def build_support_graph(checkpointer: BaseCheckpointSaver = None):
    """Constructs and compiles the SupportFlow AI LangGraph workflow for Phase 2."""
    workflow = StateGraph(AgentState)

    # 1. Add all graph nodes
    workflow.add_node("guardrail_node", guardrail_node)
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("risk_analyzer", risk_analyzer_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("response_generator", response_generator_node)
    workflow.add_node("escalation_node", escalation_node)

    # 2. Entry point: start at safety guardrail
    workflow.add_edge(START, "guardrail_node")

    # 3. Guardrail conditional routing
    workflow.add_conditional_edges(
        "guardrail_node",
        route_guardrail,
        {
            "intent_classifier": "intent_classifier",
            "__end__": END,
        },
    )

    # 4. Intent classification to risk analysis
    workflow.add_edge("intent_classifier", "risk_analyzer")

    # 5. Risk-based conditional branching
    workflow.add_conditional_edges(
        "risk_analyzer",
        route_by_risk,
        {
            "escalation_node": "escalation_node",
            "tool_node": "tool_node",
        },
    )

    # 6. Standard flow: Tool Execution -> RAG Knowledge -> Grounded Response Generator
    workflow.add_edge("tool_node", "rag_node")
    workflow.add_edge("rag_node", "response_generator")
    workflow.add_edge("response_generator", END)
    workflow.add_edge("escalation_node", END)

    # 7. Compile with conversation memory checkpointer
    active_checkpointer = checkpointer or get_checkpointer()
    app = workflow.compile(checkpointer=active_checkpointer)
    logger.info("Successfully compiled SupportFlow AI LangGraph workflow (Phase 2).")
    return app


# Singleton compiled graph instance
support_flow_app = build_support_graph()
