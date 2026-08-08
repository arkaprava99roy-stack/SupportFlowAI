"""Response generator node: synthesizes grounded answers with citations and tool results."""
import os
from typing import Dict, Any, List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agent.state import AgentState
from src.agent.nodes.intent_classifier import get_latest_user_message
from src.agent.tools.ticket_tools import enqueue_pending_review
from src.config import settings
from src.utils.logger import logger

SYSTEM_PROMPT = """You are SupportFlow AI, an intelligent, empathetic, and highly accurate customer support specialist.

Your task is to answer the customer's question directly, clearly, and helpfully using the provided Knowledge Base excerpts.

GUIDELINES:
1. Grounding: Answer strictly using facts from the Knowledge Base context. Do not invent policies.
2. Tone: Warm, empathetic, concise, and professional.
3. Formatting: Use bullet points, bold text, and numbered steps where appropriate for scannability.
4. Transparency: If the knowledge base does not contain enough information, explain what is available and offer to connect them with human support.
5. If the risk level is MEDIUM, add a reassurance note that our support team is monitoring this thread.
"""


def build_context_string(retrieved_docs: List[Dict[str, Any]]) -> str:
    """Formats retrieved document chunks into a contextual prompt block."""
    if not retrieved_docs:
        return "No specific knowledge base documents retrieved."

    context_blocks = []
    for idx, item in enumerate(retrieved_docs, start=1):
        meta = item.get("metadata", {})
        doc_name = meta.get("document", "doc.md")
        category = meta.get("category", "GENERAL")
        content = item.get("content", "")
        context_blocks.append(
            f"--- [Document #{idx}: {doc_name} | Category: {category}] ---\n{content}\n"
        )
    return "\n".join(context_blocks)


def format_order_response(order_data: Dict[str, Any]) -> str:
    """Formats retrieved order information into a clean customer response."""
    status_icon = "🚚" if order_data.get("status") == "SHIPPED" else "📦" if order_data.get("status") == "PROCESSING" else "✅" if order_data.get("status") == "DELIVERED" else "❌"

    return (
        f"{status_icon} **Order Status: {order_data.get('order_id')}**\n\n"
        f"• **Product**: {order_data.get('product_name')}\n"
        f"• **Current Status**: `{order_data.get('status')}`\n"
        f"• **Total Amount**: {order_data.get('total_amount')}\n"
        f"• **Carrier**: {order_data.get('carrier')}\n"
        f"• **Tracking Number**: `{order_data.get('tracking_number')}`\n"
        f"• **Shipping Address**: {order_data.get('shipping_address')}\n"
        f"• **Order Date**: {order_data.get('order_date')}\n\n"
        "Please let me know if you would like me to help you track this shipment, request a cancellation, or update details!"
    )


def response_generator_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node: generates final AI answer grounded with citations and tool outputs."""
    # 1. Check if tool was executed
    tool_results = state.get("tool_results", []) or []
    if tool_results:
        first_tool = tool_results[0]
        # Confirmation prompt required
        if first_tool.get("requires_confirmation"):
            msg = first_tool.get("message", "Confirmation required.")
            return {
                "messages": [AIMessage(content=msg)],
                "response_text": msg,
                "is_escalated": False,
            }

        # Order lookup success
        if first_tool.get("success") and "order_id" in first_tool and first_tool.get("status") != "CANCELLED":
            resp = format_order_response(first_tool)
            return {
                "messages": [AIMessage(content=resp)],
                "response_text": resp,
                "is_escalated": False,
            }

        # Tool message already crafted (e.g. cancellation success or unauthorized error)
        if first_tool.get("message"):
            resp = first_tool.get("message")
            return {
                "messages": [AIMessage(content=resp)],
                "response_text": resp,
                "is_escalated": False,
            }

    # 2. Standard RAG Knowledge Base Generation
    user_message = get_latest_user_message(state.get("messages", []))
    intent = state.get("intent", "GENERAL") or "GENERAL"
    risk_level = state.get("risk_level", "LOW") or "LOW"
    retrieved_docs = state.get("retrieved_docs", []) or []
    user_id = state.get("user_id", "user_demo") or "user_demo"
    conversation_id = state.get("conversation_id", "session_direct") or "session_direct"

    # Enqueue MEDIUM risk events for supervisor review
    if risk_level == "MEDIUM":
        enqueue_pending_review(
            user_id=user_id,
            conversation_id=conversation_id,
            intent=intent,
            risk_level="MEDIUM",
            user_message=user_message,
            ai_recommended_action="Supervisor review: verify dispute status, customer satisfaction, or refund eligibility.",
        )

    context_str = build_context_string(retrieved_docs)

    if settings.has_valid_api_key:
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL_NAME,
                temperature=settings.LLM_TEMPERATURE,
                api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"),
            )

            prompt_messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                SystemMessage(
                    content=f"Knowledge Base Context:\n{context_str}\n\nAssigned Intent: {intent}\nRisk Level: {risk_level}"
                ),
            ]

            for msg in state.get("messages", [])[-6:]:
                prompt_messages.append(msg)

            ai_response = llm.invoke(prompt_messages)
            response_text = str(ai_response.content)

            if risk_level == "MEDIUM" and "review" not in response_text.lower():
                response_text += "\n\n*(Note: A senior support specialist will review this interaction to ensure complete resolution.)*"

            logger.info("Successfully generated grounded LLM response with citations.")
            return {
                "messages": [AIMessage(content=response_text)],
                "response_text": response_text,
                "is_escalated": False,
            }
        except Exception as e:
            logger.warning(f"LLM generation failed ({e}). Using grounded fallback generator.")

    # Offline / Deterministic Fallback Generator
    if retrieved_docs:
        top_doc = retrieved_docs[0]
        meta = top_doc.get("metadata", {})
        title = meta.get("title", "Policy Document")
        doc_name = meta.get("document", "support_doc.md")
        excerpt = top_doc.get("content", "")[:350].strip()

        response_text = (
            f"Thank you for contacting SupportFlow AI regarding your **{intent}** inquiry.\n\n"
            f"According to our **{title}** (`{doc_name}`):\n\n"
            f"> {excerpt}...\n\n"
            f"Please let me know if you would like me to clarify any part of this or assist you with next steps!"
        )
    else:
        response_text = (
            f"Thank you for reaching out to SupportFlow AI! I've noted your question regarding **{intent}**.\n"
            "How else may I assist you with your account or order today?"
        )

    if risk_level == "MEDIUM":
        response_text += "\n\n*(Note: This issue has been flagged for expedited supervisor review to ensure everything is resolved smoothly.)*"

    return {
        "messages": [AIMessage(content=response_text)],
        "response_text": response_text,
        "is_escalated": False,
    }
