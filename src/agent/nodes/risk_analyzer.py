"""Risk analysis and safety scoring node for SupportFlow AI."""
import os
import re
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

from src.agent.state import AgentState, RiskLevel
from src.agent.nodes.intent_classifier import get_latest_user_message
from src.config import settings
from src.utils.logger import logger


class RiskAnalysisResult(BaseModel):
    """Structured output for risk analysis."""
    risk_level: RiskLevel = Field(
        description="Assigned risk level: LOW (standard inquiry), MEDIUM (billing dispute / moderate sensitivity), HIGH (security breach, compromised account, fraud, legal threat)."
    )
    risk_score: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Numeric risk probability score from 0.0 to 1.0.",
    )
    risk_reason: str = Field(
        description="Detailed explanation of the safety or risk factors identified."
    )


# High risk security patterns
HIGH_RISK_PATTERNS = [
    r"compromised",
    r"hacked",
    r"unauthorized\s+(access|login|charge|transaction)",
    r"someone\s+(logged|accessed|stole|changed)",
    r"account\s+takeover",
    r"identity\s+theft",
    r"breach",
    r"stolen\s+(card|password|account)",
    r"russia|china|nigeria|unknown\s+ip",
    r"lawsuit|lawyer|sue\s+you|attorney",
    r"credit\s+card\s+fraud",
    r"emergency\s+freeze",
]

# Medium risk patterns
MEDIUM_RISK_PATTERNS = [
    r"duplicate\s+charge",
    r"charged\s+twice",
    r"dispute",
    r"chargeback",
    r"unacceptable",
    r"furious|angry|horrible\s+service",
    r"never\s+received\s+my\s+refund",
    r"escalate\s+to\s+manager",
    r"supervisor",
    r"overcharged",
]


def rule_based_risk_analyzer(user_message: str, intent: str) -> RiskAnalysisResult:
    """Deterministic pattern matching risk evaluator for test suites & fallback."""
    text_lower = user_message.lower()

    # Check HIGH risk conditions
    if intent == "SECURITY":
        return RiskAnalysisResult(
            risk_level="HIGH",
            risk_score=0.95,
            risk_reason="Security-related intent detected (account compromise/fraud risk).",
        )

    for pattern in HIGH_RISK_PATTERNS:
        if re.search(pattern, text_lower):
            return RiskAnalysisResult(
                risk_level="HIGH",
                risk_score=0.92,
                risk_reason=f"Triggered high-severity security pattern: '{pattern}'.",
            )

    # Check MEDIUM risk conditions
    if intent in ("BILLING", "REFUND"):
        for pattern in MEDIUM_RISK_PATTERNS:
            if re.search(pattern, text_lower):
                return RiskAnalysisResult(
                    risk_level="MEDIUM",
                    risk_score=0.60,
                    risk_reason=f"Billing/refund dispute pattern detected: '{pattern}'.",
                )

    for pattern in MEDIUM_RISK_PATTERNS:
        if re.search(pattern, text_lower):
            return RiskAnalysisResult(
                risk_level="MEDIUM",
                risk_score=0.55,
                risk_reason=f"Customer frustration or escalation trigger detected: '{pattern}'.",
            )

    # Default to LOW risk
    return RiskAnalysisResult(
        risk_level="LOW",
        risk_score=0.10,
        risk_reason="Standard informational inquiry without security or dispute indicators.",
    )


RISK_PROMPT = """You are a real-time risk & safety evaluator for SupportFlow AI.
Analyze the user's message and current intent to score the risk level:

1. HIGH (score 0.80 - 1.0):
   - Account takeover, unauthorized login, credentials stolen, fraud, security breach.
   - Legal threats, harassment, severe safety concerns.
   - Demands for immediate account freeze or investigation.

2. MEDIUM (score 0.40 - 0.79):
   - Billing disputes, duplicate charges, chargeback threats, high-value refund complaints.
   - Significant customer dissatisfaction requiring managerial review.

3. LOW (score 0.0 - 0.39):
   - Routine support questions (shipping policies, return guides, password reset instructions, FAQ).
   - Informational requests easily resolved by knowledge base.

Respond with structured JSON matching RiskAnalysisResult."""


def risk_analyzer_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node: evaluates risk and safety level of the user request."""
    user_message = get_latest_user_message(state.get("messages", []))
    intent = state.get("intent", "GENERAL") or "GENERAL"

    if settings.has_valid_api_key:
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL_NAME,
                temperature=settings.LLM_TEMPERATURE,
                api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"),
            )
            structured_llm = llm.with_structured_output(RiskAnalysisResult)
            result = structured_llm.invoke([
                SystemMessage(content=RISK_PROMPT),
                HumanMessage(content=f"Intent: {intent}\nUser Message: {user_message}"),
            ])
            logger.info(f"Risk analyzed by LLM: {result.risk_level} (score: {result.risk_score:.2f}) - {result.risk_reason}")
            return {
                "risk_level": result.risk_level,
                "risk_score": result.risk_score,
                "risk_reason": result.risk_reason,
            }
        except Exception as e:
            logger.warning(f"LLM risk analysis failed ({e}). Falling back to rule-based analyzer.")

    # Fallback / offline mode
    fallback_res = rule_based_risk_analyzer(user_message, intent)
    logger.info(f"Risk analyzed by rules: {fallback_res.risk_level} (score: {fallback_res.risk_score:.2f}) - {fallback_res.risk_reason}")
    return {
        "risk_level": fallback_res.risk_level,
        "risk_score": fallback_res.risk_score,
        "risk_reason": fallback_res.risk_reason,
    }
