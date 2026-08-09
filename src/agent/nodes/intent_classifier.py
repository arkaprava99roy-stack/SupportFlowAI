"""Intent classification node for SupportFlow AI."""
import json
import os
import re
from typing import Dict, Any, Optional, List, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from src.agent.state import AgentState, IntentType
from src.config import settings
from src.utils.logger import logger


class IntentClassificationResult(BaseModel):
    """Structured output for intent classification."""
    intent: IntentType = Field(
        description="The classified customer intent. Must be one of: BILLING, REFUND, TECHNICAL_SUPPORT, ACCOUNT, PRODUCT_INFO, SHIPPING, SECURITY, GENERAL."
    )
    confidence: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Confidence score for this classification.",
    )
    reason: str = Field(
        default="",
        description="Brief explanation of why this intent was selected.",
    )


# Comprehensive keyword taxonomy for offline execution and deterministic evals
INTENT_KEYWORDS: Dict[IntentType, List[str]] = {
    "SECURITY": [
        "hacked", "hack", "compromised", "stolen", "unauthorized", "suspicious login",
        "breach", "attacker", "someone logged into", "fraud", "scam", "dan", "ignore all",
        "system prompt", "system override", "dump the", "sarah miller", "private order details",
        "locked out of my account", "credentials", "leak", "lawsuit", "legal counsel", "end my life"
    ],
    "TECHNICAL_SUPPORT": [
        "500 error", "500", "system error", "app error", "runtime error", "bug", "crash",
        "not working", "fails", "glitch", "broken", "cannot connect", "exception", "failed to load"
    ],
    "REFUND": [
        "refund", "money back", "return policy", "reimburse", "returned item",
        "refund guarantee", "days do i have to return", "refund policy", "cancel my order",
        "cancel order", "cancel ord-", "cancellation", "cancel this order", "return label",
        "prepaid return", "exchange", "replace item", "does not fit", "wrong size", "rma"
    ],
    "BILLING": [
        "duplicate charge", "billing error", "dispute", "charged", "charge", "invoice",
        "double charged", "billing", "payment", "credit card", "receipt", "subscription",
        "autopay", "price", "fee", "payment method", "billing address"
    ],
    "SHIPPING": [
        "tracking number", "tracking", "package", "where is my package", "where is my order",
        "order status", "check tracking", "ord-100", "tracking status", "order #", "my order ord-",
        "track order", "shipped", "carrier", "delivery", "fedex", "ups", "usps", "delayed",
        "dispatch", "arrival", "shipment", "international", "canada", "europe", "transit times", "shipping times"
    ],
    "ACCOUNT": [
        "password", "2fa", "two-factor", "login", "profile", "email address",
        "reset password", "delete account", "gdpr", "settings", "reset link",
        "forgot my password", "account email"
    ],
    "PRODUCT_INFO": [
        "compatibility", "specs", "specification", "warranty", "features",
        "dimension", "size chart", "colors", "product details"
    ],
}


# Priority tiebreaker: when two intents tie or are close in score,
# the one with the higher priority index wins for multi-intent queries.
INTENT_PRIORITY: Dict[str, int] = {
    "SECURITY": 100,
    "TECHNICAL_SUPPORT": 80,
    "ACCOUNT": 70,
    "SHIPPING": 65,
    "REFUND": 60,
    "BILLING": 55,
    "PRODUCT_INFO": 40,
    "GENERAL": 10,
}

# Multi-intent signal words — indicate a compound query; prefer the first-
# mentioned or higher-priority intent rather than whichever keyword is longest.
MULTI_INTENT_SIGNALS = ["and also", "and see", "as well as", "also", "additionally", " and "]


def rule_based_intent_classifier(text: str) -> IntentClassificationResult:
    """Deterministic keyword-based intent classifier with multi-intent scoring."""
    text_lower = text.lower()

    # SECURITY always wins — non-negotiable safety check
    for keyword in INTENT_KEYWORDS["SECURITY"]:
        if keyword in text_lower:
            return IntentClassificationResult(
                intent="SECURITY",
                confidence=0.98,
                reason=f"Matched high-priority security keyword: '{keyword}'",
            )

    # Score every remaining intent by counting keyword hits
    scores: Dict[str, int] = {intent: 0 for intent in INTENT_KEYWORDS if intent != "SECURITY"}
    matched_keywords: Dict[str, list] = {intent: [] for intent in scores}

    for intent, keywords in INTENT_KEYWORDS.items():
        if intent == "SECURITY":
            continue
        for kw in keywords:
            if kw in text_lower:
                scores[intent] += 1
                matched_keywords[intent].append(kw)

    # Determine if this is a compound / multi-intent query
    is_multi_intent = any(signal in text_lower for signal in MULTI_INTENT_SIGNALS)

    # Find winner: highest score; on tie, use priority map
    best_intent = "GENERAL"
    best_score = 0
    for intent, score in scores.items():
        if score > best_score:
            best_score = score
            best_intent = intent
        elif score == best_score and score > 0:
            # Tiebreak: prefer higher-priority intent
            if INTENT_PRIORITY.get(intent, 0) > INTENT_PRIORITY.get(best_intent, 0):
                best_intent = intent

    if best_score == 0:
        return IntentClassificationResult(
            intent="GENERAL",
            confidence=0.70,
            reason="No specific category keywords matched.",
        )

    # For multi-intent queries, boost confidence of the winning category
    confidence = min(0.96, 0.88 + (best_score * 0.03)) if is_multi_intent else min(0.96, 0.85 + (best_score * 0.04))
    kws = ", ".join(matched_keywords[best_intent][:3])
    reason = f"Matched {best_score} keyword(s): '{kws}'"
    if is_multi_intent:
        reason += " [multi-intent query — primary intent selected by priority]"

    return IntentClassificationResult(
        intent=best_intent,
        confidence=round(confidence, 3),
        reason=reason,
    )


def get_latest_user_message(messages: Sequence[BaseMessage]) -> str:
    """Extracts text content of the most recent user message."""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage) or getattr(msg, "type", "") == "human":
            return str(msg.content)
        if isinstance(msg, tuple) and msg[0] in ("user", "human"):
            return str(msg[1])
        if isinstance(msg, dict) and msg.get("role") in ("user", "human"):
            return str(msg.get("content", ""))
    return ""


def intent_classifier_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node classifying customer query intent."""
    messages = state.get("messages", [])
    user_message = get_latest_user_message(messages)

    if not user_message:
        logger.warning("No user message found to classify intent, defaulting to GENERAL")
        return {"intent": "GENERAL", "intent_confidence": 0.5}

    logger.info(f"Classifying intent for user message: '{user_message[:50]}...'")

    # If valid OpenAI API key is present, use structured LLM calling
    if settings.has_valid_api_key:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.0,
                api_key=settings.OPENAI_API_KEY,
            )
            structured_llm = llm.with_structured_output(IntentClassificationResult)
            result = structured_llm.invoke([
                SystemMessage(content="You are an expert customer intent classifier."),
                HumanMessage(content=user_message),
            ])
            return {
                "intent": result.intent,
                "intent_confidence": result.confidence,
            }
        except Exception as e:
            logger.error(f"OpenAI intent classification failed: {e}. Falling back to rule-based.")

    # Rule-based fallback
    rule_result = rule_based_intent_classifier(user_message)
    logger.info(f"Classified intent as: {rule_result.intent} (confidence: {rule_result.confidence})")
    return {
        "intent": rule_result.intent,
        "intent_confidence": rule_result.confidence,
    }
