"""RAG faithfulness and source relevance evaluator."""
from typing import List, Dict, Any


def evaluate_rag_sources(expected_sources: List[str], retrieved_citations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Scores source citation precision and recall."""
    if not expected_sources:
        # Non-RAG query (e.g. prompt injection, transactional tool, gibberish)
        return {
            "score": 1.0,
            "precision": 1.0,
            "recall": 1.0,
            "is_applicable": False,
            "retrieved_count": len(retrieved_citations),
        }

    retrieved_docs = [c.get("document", "") for c in retrieved_citations]

    # Check if expected source documents were retrieved
    hits = sum(1 for exp in expected_sources if any(exp.lower() in r.lower() for r in retrieved_docs))
    recall = hits / len(expected_sources) if expected_sources else 1.0
    precision = hits / len(retrieved_docs) if retrieved_docs else 0.0

    # Score: Full credit if relevant expected doc found, partial for multiple
    score = 1.0 if hits >= 1 else 0.0

    return {
        "score": score,
        "recall": round(recall, 2),
        "precision": round(precision, 2),
        "is_applicable": True,
        "expected": expected_sources,
        "retrieved": retrieved_docs,
    }
