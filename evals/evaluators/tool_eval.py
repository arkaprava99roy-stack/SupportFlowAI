"""Tool calling correctness evaluator."""
from typing import List, Dict, Any


def evaluate_tool_calling(expected_tools: List[str], actual_tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Scores whether expected tools were invoked correctly."""
    if not expected_tools:
        # Non-tool query - shouldn't call unauthorized mutations
        score = 1.0 if len(actual_tools) == 0 else 0.8
        return {
            "score": score,
            "correct": len(actual_tools) == 0,
            "expected": [],
            "actual": [t.get("tool", "") for t in actual_tools],
        }

    actual_names = [t.get("tool", "") for t in actual_tools]
    hits = sum(1 for exp in expected_tools if any(exp in act for act in actual_names))

    score = hits / len(expected_tools) if expected_tools else 1.0
    return {
        "score": round(score, 2),
        "correct": hits == len(expected_tools),
        "expected": expected_tools,
        "actual": actual_names,
    }
