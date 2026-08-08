"""Intent classification evaluator."""
from typing import Dict, Any


def evaluate_intent(expected_intent: str, predicted_intent: str) -> Dict[str, Any]:
    """Scores intent classification against expected ground truth."""
    if not expected_intent:
        return {"score": 1.0, "match": True, "expected": "", "predicted": predicted_intent}

    is_match = expected_intent.upper() == predicted_intent.upper()
    # Partial allowance for related categories (e.g. REFUND vs RETURN)
    partial_match = False
    if not is_match:
        if expected_intent.upper() in ["REFUND", "RETURN"] and predicted_intent.upper() in ["REFUND", "RETURN"]:
            partial_match = True

    score = 1.0 if is_match else (0.85 if partial_match else 0.0)
    return {
        "score": score,
        "match": is_match or partial_match,
        "expected": expected_intent,
        "predicted": predicted_intent,
    }
