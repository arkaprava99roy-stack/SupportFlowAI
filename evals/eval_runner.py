"""Automated evaluation runner executing the 25+ benchmark suite across SupportFlow AI."""
import os
import json
import time
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from src.agent.graph import support_flow_app
from src.observability.tracer import start_trace
from src.db.seed import seed_database
from evals.evaluators.intent_eval import evaluate_intent
from evals.evaluators.rag_eval import evaluate_rag_sources
from evals.evaluators.tool_eval import evaluate_tool_calling
from evals.evaluators.guardrail_eval import evaluate_guardrails
from evals.report_generator import generate_markdown_report, REPORT_PATH
from src.config import settings

DATASET_PATH = os.path.join(settings.BASE_DIR, "evals", "dataset.json")


def load_dataset() -> List[Dict[str, Any]]:
    """Loads benchmark test dataset from JSON."""
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_eval_suite() -> Dict[str, Any]:
    """Executes the full evaluation suite and records telemetry and scores."""
    print("=" * 70)
    print(">> SupportFlow AI -- Automated Benchmark & Evaluation Runner")
    print("=" * 70)

    # Initialize and seed database
    seed_database()
    dataset = load_dataset()
    print(f"Loaded {len(dataset)} curated test cases from {DATASET_PATH}\n")

    results = []
    total_latency_ms = 0.0

    for i, test in enumerate(dataset, 1):
        test_id = test["id"]
        category = test.get("category", "General")
        input_msg = test["input_message"]
        exp_intent = test.get("expected_intent", "")
        exp_sources = test.get("expected_sources", [])
        exp_tools = test.get("expected_tools", [])
        should_escalate = test.get("should_escalate", False)
        is_injection = test.get("is_injection", False)

        # Start Telemetry Trace
        tracer = start_trace(trace_id=f"eval_{test_id}", user_id="user_demo")
        tracer.log_input(input_msg)

        start_time = time.time()
        config = {"configurable": {"thread_id": f"eval_thread_{test_id}"}}
        state_input = {
            "user_id": "user_demo",
            "conversation_id": f"eval_conv_{test_id}",
            "messages": [HumanMessage(content=input_msg)],
        }

        # Invoke Agent Graph
        agent_result = support_flow_app.invoke(state_input, config=config)
        elapsed_ms = (time.time() - start_time) * 1000
        total_latency_ms += elapsed_ms

        pred_intent = agent_result.get("intent", "GENERAL")
        if agent_result.get("is_safe") is False or agent_result.get("guardrail_violation"):
            pred_intent = "SECURITY"

        act_risk = agent_result.get("risk_level", "LOW")
        act_citations = agent_result.get("citations", []) or []
        act_tools = agent_result.get("tool_calls", []) or []
        is_escalated = agent_result.get("is_escalated", False)
        ticket_id = agent_result.get("ticket_id")

        resp_text = agent_result.get("response_text", "")
        if not resp_text and agent_result.get("messages"):
            resp_text = str(agent_result["messages"][-1].content)

        # Finalize telemetry trace
        tracer.record_output(
            response_text=resp_text,
            intent=pred_intent,
            risk_level=act_risk,
            citations=act_citations,
            is_escalated=is_escalated,
            ticket_id=ticket_id,
        )
        tracer.finalize()

        # Score Evaluators
        i_eval = evaluate_intent(exp_intent, pred_intent)
        r_eval = evaluate_rag_sources(exp_sources, act_citations)
        t_eval = evaluate_tool_calling(exp_tools, act_tools)
        g_eval = evaluate_guardrails(is_injection, should_escalate, act_risk, is_escalated, resp_text)

        test_result = {
            "id": test_id,
            "category": category,
            "input_message": input_msg,
            "expected_intent": exp_intent,
            "predicted_intent": pred_intent,
            "actual_risk": act_risk,
            "actual_tools": act_tools,
            "retrieved_sources": [c.get("document", "") for c in act_citations],
            "latency_ms": round(elapsed_ms, 1),
            "intent_eval": i_eval,
            "rag_eval": r_eval,
            "tool_eval": t_eval,
            "guardrail_eval": g_eval,
        }
        results.append(test_result)

        status_flag = "[PASS]" if (i_eval["match"] and g_eval["passed"] and t_eval["score"] >= 0.8) else "[FAIL]"
        print(f"[{i:02d}/{len(dataset)}] {status_flag} | {category:20s} | ID: {test_id:22s} | Intent: {pred_intent:12s} ({round(elapsed_ms)}ms)")

    # Aggregate Benchmark Statistics
    total = len(results)
    intent_accuracy = (sum(r["intent_eval"]["score"] for r in results) / total) * 100
    rag_applicable = [r for r in results if r["rag_eval"]["is_applicable"]]
    rag_relevance = (sum(r["rag_eval"]["score"] for r in rag_applicable) / len(rag_applicable) * 100) if rag_applicable else 100.0
    guardrail_accuracy = (sum(r["guardrail_eval"]["score"] for r in results) / total) * 100
    tool_accuracy = (sum(r["tool_eval"]["score"] for r in results) / total) * 100
    avg_latency = total_latency_ms / total

    summary_stats = {
        "total_tests": total,
        "intent_accuracy": round(intent_accuracy, 2),
        "rag_relevance": round(rag_relevance, 2),
        "guardrail_accuracy": round(guardrail_accuracy, 2),
        "tool_accuracy": round(tool_accuracy, 2),
        "avg_latency_ms": round(avg_latency, 2),
    }

    # Generate Markdown Report
    generate_markdown_report(results, summary_stats)

    print("\n" + "=" * 70)
    print("EVALUATION BENCHMARK SCORECARD")
    print("=" * 70)
    print(f"Intent Classification Accuracy : {intent_accuracy:6.2f}%  (Target: >= 90%) -> {'[PASS]' if intent_accuracy >= 90 else '[FAIL]'}")
    print(f"RAG Faithfulness & Relevance   : {rag_relevance:6.2f}%  (Target: >= 85%) -> {'[PASS]' if rag_relevance >= 85 else '[FAIL]'}")
    print(f"Guardrail Precision & Recall   : {guardrail_accuracy:6.2f}%  (Target: >= 95%) -> {'[PASS]' if guardrail_accuracy >= 95 else '[FAIL]'}")
    print(f"Tool Calling Correctness       : {tool_accuracy:6.2f}%  (Target: >= 95%) -> {'[PASS]' if tool_accuracy >= 95 else '[FAIL]'}")
    print(f"Average Agent Latency          : {avg_latency:6.2f}ms (Target: <= 2000ms)")
    print("=" * 70)
    print(f"Full Markdown Report saved to: {REPORT_PATH}\n")

    return summary_stats


if __name__ == "__main__":
    run_eval_suite()
