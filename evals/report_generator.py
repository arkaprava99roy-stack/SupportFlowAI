"""Markdown report generator for SupportFlow AI evaluation results."""
import os
import datetime
from typing import List, Dict, Any
from src.config import settings

RESULTS_DIR = os.path.join(settings.BASE_DIR, "evals", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)
REPORT_PATH = os.path.join(RESULTS_DIR, "eval_report.md")


def generate_markdown_report(results: List[Dict[str, Any]], summary_stats: Dict[str, Any]) -> str:
    """Creates a comprehensive benchmark report with pass/fail scorecards."""
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    intent_acc = summary_stats.get("intent_accuracy", 0.0)
    rag_rel = summary_stats.get("rag_relevance", 0.0)
    guardrail_acc = summary_stats.get("guardrail_accuracy", 0.0)
    tool_acc = summary_stats.get("tool_accuracy", 0.0)
    avg_latency = summary_stats.get("avg_latency_ms", 0.0)
    total_tests = len(results)

    # Pass/fail targets
    intent_pass = intent_acc >= 90.0
    rag_pass = rag_rel >= 85.0
    guardrail_pass = guardrail_acc >= 95.0
    tool_pass = tool_acc >= 95.0
    overall_pass = intent_pass and rag_pass and guardrail_pass and tool_pass

    lines = []
    lines.append("# SupportFlow AI — Automated Evaluation & Benchmark Report")
    lines.append(f"\n> **Generated:** `{now_str}`  ")
    lines.append(f"> **Total Test Cases:** `{total_tests}`  ")
    lines.append(f"> **Overall Benchmark Status:** **{'✅ PASS' if overall_pass else '⚠️ REVIEW REQUIRED'}**\n")

    lines.append("## 🏆 Benchmark Scorecard & Target SLAs\n")
    lines.append("| Metric Domain | Target SLA | Actual Score | Status | Description |")
    lines.append("| :--- | :---: | :---: | :---: | :--- |")
    lines.append(f"| **Intent Classification** | $\\ge 90\\%$ | **{intent_acc:.1f}%** | {'✅ PASS' if intent_pass else '❌ FAIL'} | Accuracy across 8 intent taxonomies |")
    lines.append(f"| **RAG Faithfulness & Relevance** | $\\ge 85\\%$ | **{rag_rel:.1f}%** | {'✅ PASS' if rag_pass else '❌ FAIL'} | Document citation precision and recall |")
    lines.append(f"| **Guardrail & Safety Recall** | $\\ge 95\\%$ | **{guardrail_acc:.1f}%** | {'✅ PASS' if guardrail_pass else '❌ FAIL'} | Injection refusal & high-risk ticket escalation |")
    lines.append(f"| **Tool Calling Accuracy** | $\\ge 95\\%$ | **{tool_acc:.1f}%** | {'✅ PASS' if tool_pass else '❌ FAIL'} | Parameter extraction & safe tool gating |")
    lines.append(f"| **Average Latency** | $\\le 2000\\text{{ms}}$ | **{avg_latency:.1f}ms** | {'✅ PASS' if avg_latency <= 2000 else '⚠️ SLOW'} | End-to-end multi-agent execution speed |")

    lines.append("\n---\n")
    lines.append("## 📊 Performance by Evaluation Category\n")
    lines.append("| Category | Cases | Intent Acc | RAG Rel | Tool Acc | Guardrail Acc |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")

    # Group by category
    categories = sorted(list(set(r.get("category", "General") for r in results)))
    for cat in categories:
        cat_items = [r for r in results if r.get("category") == cat]
        c_len = len(cat_items)
        c_intent = (sum(r["intent_eval"]["score"] for r in cat_items) / c_len) * 100
        rag_applicable = [r for r in cat_items if r["rag_eval"]["is_applicable"]]
        c_rag = (sum(r["rag_eval"]["score"] for r in rag_applicable) / len(rag_applicable) * 100) if rag_applicable else 100.0
        c_tool = (sum(r["tool_eval"]["score"] for r in cat_items) / c_len) * 100
        c_guard = (sum(r["guardrail_eval"]["score"] for r in cat_items) / c_len) * 100

        lines.append(f"| **{cat}** | {c_len} | {c_intent:.1f}% | {c_rag:.1f}% | {c_tool:.1f}% | {c_guard:.1f}% |")

    lines.append("\n---\n")
    lines.append("## 🧪 Detailed Test Case Results\n")
    lines.append("| Test ID | Category | Expected Intent | Actual Intent | Risk | Tools | RAG Sources | Status |")
    lines.append("| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: |")

    for r in results:
        t_id = r["id"]
        t_cat = r.get("category", "FAQ")
        exp_i = r.get("expected_intent", "")
        act_i = r.get("predicted_intent", "")
        risk = r.get("actual_risk", "LOW")
        tools_str = ", ".join(t.get("tool", "") for t in r.get("actual_tools", [])) or "None"
        sources_str = ", ".join(r.get("retrieved_sources", [])) or "None"
        
        passed = (
            r["intent_eval"]["score"] >= 0.85
            and r["rag_eval"]["score"] >= 0.8
            and r["guardrail_eval"]["passed"]
            and r["tool_eval"]["score"] >= 0.8
        )
        status_icon = "✅ Pass" if passed else "❌ Review"

        lines.append(f"| `{t_id}` | {t_cat} | `{exp_i}` | `{act_i}` | `{risk}` | `{tools_str}` | {sources_str} | {status_icon} |")

    lines.append("\n---\n")
    lines.append("## 🔍 Telemetry & Observability Diagnostics\n")
    lines.append("- **Local Trace Log:** `logs/traces.jsonl`")
    lines.append("- **Audit Log Table:** PostgreSQL / SQLite `tool_audit_logs`")
    lines.append("- **Human-in-the-Loop Review Queue:** `pending_reviews` table")
    lines.append("- **Cloud Export:** LangSmith / OpenTelemetry tracing ready via `LANGSMITH_API_KEY`\n")

    report_content = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_content
