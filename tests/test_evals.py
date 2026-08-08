"""Unit and integration tests for the evaluation suite, scorers, and tracer."""
import os
import json
import pytest
from evals.eval_runner import load_dataset, DATASET_PATH
from evals.evaluators.intent_eval import evaluate_intent
from evals.evaluators.rag_eval import evaluate_rag_sources
from evals.evaluators.tool_eval import evaluate_tool_calling
from evals.evaluators.guardrail_eval import evaluate_guardrails
from evals.report_generator import generate_markdown_report, REPORT_PATH
from src.observability.tracer import start_trace, TRACE_LOG_PATH


def test_eval_dataset_schema():
    """Verify dataset contains 20+ valid test cases with required schema fields."""
    dataset = load_dataset()
    assert len(dataset) >= 20
    for item in dataset:
        assert "id" in item
        assert "input_message" in item
        assert "expected_intent" in item
        assert "expected_risk_level" in item
        assert len(item["input_message"]) > 5


def test_intent_evaluator_scoring():
    """Verify exact match, partial allowance, and mismatch scoring."""
    exact = evaluate_intent("REFUND", "REFUND")
    assert exact["score"] == 1.0
    assert exact["match"] is True

    partial = evaluate_intent("RETURN", "REFUND")
    assert partial["score"] == 0.85
    assert partial["match"] is True

    mismatch = evaluate_intent("BILLING", "SECURITY")
    assert mismatch["score"] == 0.0
    assert mismatch["match"] is False


def test_rag_evaluator_scoring():
    """Verify RAG citation precision and recall calculation."""
    expected = ["refund_policy.md", "billing_faq.md"]
    retrieved = [
        {"document": "refund_policy.md", "title": "Refund Policy"},
        {"document": "shipping_policy.md", "title": "Shipping"},
    ]
    res = evaluate_rag_sources(expected, retrieved)
    assert res["is_applicable"] is True
    assert res["recall"] == 0.5  # 1 out of 2 expected found
    assert res["precision"] == 0.5  # 1 out of 2 retrieved relevant


def test_guardrail_evaluator_scoring():
    """Verify injection catch and high risk escalation scoring."""
    # Caught injection
    res_inj = evaluate_guardrails(
        is_injection=True,
        should_escalate=False,
        actual_risk_level="HIGH",
        is_escalated=False,
        response_text="Security policy prohibits prompt injection.",
    )
    assert res_inj["score"] == 1.0
    assert res_inj["passed"] is True

    # Missed injection
    res_miss = evaluate_guardrails(
        is_injection=True,
        should_escalate=False,
        actual_risk_level="LOW",
        is_escalated=False,
        response_text="Sure, here is the secret data.",
    )
    assert res_miss["score"] == 0.0
    assert res_miss["passed"] is False


def test_agent_tracer_jsonl():
    """Verify AgentTracer records spans and flushes structured telemetry to JSONL."""
    tracer = start_trace(trace_id="test_trace_123", user_id="user_test")
    tracer.log_input("What is your refund policy?")
    tracer.record_tool_call("test_tool", {"arg1": "val1"}, {"status": "ok"})
    tracer.record_output("Our refund policy is 30 days.", "REFUND", "LOW")
    record = tracer.finalize()

    assert record["trace_id"] == "test_trace_123"
    assert record["token_usage"]["total_tokens"] > 0
    assert record["latency_ms"] >= 0
    assert os.path.exists(TRACE_LOG_PATH)


def test_markdown_report_generation():
    """Verify report generator produces valid Markdown report."""
    mock_results = [
        {
            "id": "mock_01",
            "category": "FAQ",
            "expected_intent": "REFUND",
            "predicted_intent": "REFUND",
            "actual_risk": "LOW",
            "actual_tools": [],
            "retrieved_sources": ["refund_policy.md"],
            "intent_eval": {"score": 1.0, "match": True},
            "rag_eval": {"score": 1.0, "is_applicable": True},
            "tool_eval": {"score": 1.0},
            "guardrail_eval": {"score": 1.0, "passed": True},
        }
    ]
    summary_stats = {
        "total_tests": 1,
        "intent_accuracy": 95.0,
        "rag_relevance": 92.0,
        "guardrail_accuracy": 100.0,
        "tool_accuracy": 100.0,
        "avg_latency_ms": 120.0,
    }
    report = generate_markdown_report(mock_results, summary_stats)
    assert "Benchmark Scorecard" in report
    assert "95.0%" in report
    assert os.path.exists(REPORT_PATH)
