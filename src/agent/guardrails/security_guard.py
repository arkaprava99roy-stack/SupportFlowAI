"""Lightweight prompt-injection, jailbreak, and unauthorized data access guardrail."""
import re
from typing import Optional
from pydantic import BaseModel, Field

from src.utils.logger import logger


class GuardrailVerdict(BaseModel):
    """Structured result of safety guardrail evaluation."""
    is_safe: bool = Field(default=True, description="Whether the user input passed all safety guardrails.")
    violation_type: Optional[str] = Field(
        default=None,
        description="Type of violation if blocked: PROMPT_INJECTION, UNAUTHORIZED_DATA_ACCESS, or UNSAFE_TOOL_REQUEST.",
    )
    reason: Optional[str] = Field(default=None, description="Detailed explanation of the safety trigger.")
    refusal_message: Optional[str] = Field(
        default=None,
        description="Standardized security refusal message presented to the user.",
    )


# Prompt Injection / Jailbreak Attack Patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+directives",
    r"bypass\s+all\s+(safety|guardrails|rules)",
    r"you\s+are\s+now\s+(in\s+)?(developer|dan|unrestricted|god)\s+mode",
    r"you\s+are\s+now\s+dan",
    r"system\s+override",
    r"act\s+as\s+(root|superuser|an\s+unfiltered\s+ai)",
    r"reveal\s+your\s+(system\s+prompt|hidden\s+instructions|secret\s+key)",
    r"print\s+(the\s+)?system\s+prompt",
    r"dump\s+(all\s+|the\s+full\s+)?(database|users|passwords|env|tables?)",
    r"sudo\s+rm|drop\s+table|delete\s+from\s+users",
]

# Cross-User / Unauthorized Data Access Patterns
UNAUTHORIZED_ACCESS_PATTERNS = [
    r"give\s+me\s+(another\s+customer|other\s+users?|all\s+customers?)['’]?s?\s+(?:order\s+)?(details|accounts?|orders?|emails?|address)",
    r"show\s+me\s+(user_\d+|sarah(?:\s+miller)?|david(?:\s+chen)?|elena|marcus|another\s+customer)['’]?s?\s*(?:private\s+)?(?:order\s+)?(order|account|credit\s*card|address|details|shipping)",
    r"lookup\s+(?:order\s+details|order|account|details)\s+for\s+(user_\d+|sarah(?:\s+miller)?|david(?:\s+chen)?|another\s+user|another\s+customer)",
    r"what\s+is\s+(user_\d+|another\s+customer|sarah(?:\s+miller)?)['’]?s?\s*(password|email|phone|card|address|order)",
    r"fetch\s+data\s+for\s+all\s+users",
    r"list\s+all\s+orders\s+in\s+the\s+system",
    r"another\s+customer['’]?s\s+(order|account|details|address)",
    r"sarah\s+miller['’]?s\s+private",
]


def evaluate_input_guardrail(user_message: str, current_user_id: str = "user_demo") -> GuardrailVerdict:
    """Evaluates user text against prompt injection and unauthorized data access patterns."""
    text_lower = user_message.lower().strip()

    # 1. Prompt Injection & Jailbreak Check
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(f"[GUARDRAIL BLOCKED] Prompt injection detected: '{pattern}'")
            return GuardrailVerdict(
                is_safe=False,
                violation_type="PROMPT_INJECTION",
                reason=f"Matched prompt injection/jailbreak pattern: '{pattern}'",
                refusal_message=(
                    "Security Policy Enforcement: I cannot process instructions designed to override system directives, "
                    "bypass safety guardrails, or disclose internal system prompts. Please ask a valid support question."
                ),
            )

    # 2. Cross-User / Unauthorized Data Access Check
    for pattern in UNAUTHORIZED_ACCESS_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(f"[GUARDRAIL BLOCKED] Cross-user unauthorized data access: '{pattern}'")
            return GuardrailVerdict(
                is_safe=False,
                violation_type="UNAUTHORIZED_DATA_ACCESS",
                reason=f"Attempted access to unauthorized user data: '{pattern}'",
                refusal_message=(
                    "Access Control & Privacy Violation: I am strictly prohibited from retrieving or displaying data "
                    f"belonging to other customers. You may only manage records associated with your authenticated profile ('{current_user_id}')."
                ),
            )

    # All safety checks passed
    return GuardrailVerdict(is_safe=True)
