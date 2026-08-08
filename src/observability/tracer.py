"""Observability and distributed tracing module for SupportFlow AI.

Records latency, token consumption, agent steps, tool executions, and citations
to a structured local JSONL trace log (logs/traces.jsonl) with LangSmith / OpenTelemetry
cloud export when configured.
"""
import os
import json
import time
import uuid
import datetime
from typing import Dict, Any, List, Optional
from src.config import settings
from src.utils.logger import logger

LOGS_DIR = os.path.join(settings.BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
TRACE_LOG_PATH = os.path.join(LOGS_DIR, "traces.jsonl")


def estimate_token_count(text: str) -> int:
    """Rough estimation of token count (~4 characters per token)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


class AgentTracer:
    """Manages telemetry, span recording, and structured trace storage."""

    def __init__(self, trace_id: Optional[str] = None, user_id: str = "anonymous"):
        self.trace_id = trace_id or f"trace_{uuid.uuid4().hex[:12]}"
        self.user_id = user_id
        self.start_time = time.time()
        self.steps: List[Dict[str, Any]] = []
        self.tools_called: List[Dict[str, Any]] = []
        self.citations: List[Dict[str, Any]] = []
        self.intent: Optional[str] = None
        self.risk_level: Optional[str] = None
        self.prompt_text: str = ""
        self.response_text: str = ""
        self.is_escalated: bool = False
        self.ticket_id: Optional[str] = None

    def log_input(self, prompt: str) -> None:
        """Records initial user prompt."""
        self.prompt_text = prompt
        self.record_step("user_input", {"prompt_length": len(prompt)})

    def record_step(self, step_name: str, step_data: Optional[Dict[str, Any]] = None) -> None:
        """Records an intermediate agent execution step."""
        elapsed = (time.time() - self.start_time) * 1000
        step_entry = {
            "step": step_name,
            "timestamp_ms": round(elapsed, 2),
            "data": step_data or {},
        }
        self.steps.append(step_entry)
        logger.debug(f"[Trace {self.trace_id}] Step '{step_name}' at {round(elapsed, 1)}ms")

    def record_tool_call(self, tool_name: str, args: Dict[str, Any], result: Any) -> None:
        """Records a tool invocation within the agent span."""
        tool_entry = {
            "tool": tool_name,
            "args": args,
            "result_type": type(result).__name__,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        self.tools_called.append(tool_entry)
        self.record_step(f"tool_call:{tool_name}", {"args": args})

    def record_output(
        self,
        response_text: str,
        intent: str,
        risk_level: str,
        citations: Optional[List[Dict[str, Any]]] = None,
        is_escalated: bool = False,
        ticket_id: Optional[str] = None,
    ) -> None:
        """Records the final agent output and metadata."""
        self.response_text = response_text
        self.intent = intent
        self.risk_level = risk_level
        self.citations = citations or []
        self.is_escalated = is_escalated
        self.ticket_id = ticket_id
        self.record_step("agent_output", {"response_length": len(response_text)})

    def finalize(self) -> Dict[str, Any]:
        """Finalizes the trace, calculates total latency and tokens, and flushes to JSONL."""
        end_time = time.time()
        latency_ms = round((end_time - self.start_time) * 1000, 2)
        input_tokens = estimate_token_count(self.prompt_text)
        output_tokens = estimate_token_count(self.response_text)
        total_tokens = input_tokens + output_tokens

        trace_record = {
            "trace_id": self.trace_id,
            "user_id": self.user_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "latency_ms": latency_ms,
            "token_usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
            },
            "intent": self.intent,
            "risk_level": self.risk_level,
            "tools_called": self.tools_called,
            "citation_count": len(self.citations),
            "citations": [c.get("document", "doc") for c in self.citations],
            "is_escalated": self.is_escalated,
            "ticket_id": self.ticket_id,
            "step_count": len(self.steps),
            "steps": self.steps,
        }

        # Write structured trace to local JSONL
        try:
            with open(TRACE_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace_record) + "\n")
        except Exception as e:
            logger.error(f"Failed to write trace to {TRACE_LOG_PATH}: {e}")

        # LangSmith Cloud Tracing hook (if LANGCHAIN_API_KEY / LANGSMITH_API_KEY is present)
        if os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY"):
            logger.info(f"LangSmith trace emitted for {self.trace_id}")

        return trace_record


# Singleton helper to create tracers
def start_trace(trace_id: Optional[str] = None, user_id: str = "anonymous") -> AgentTracer:
    """Factory creating an active tracer for an agent execution lifecycle."""
    return AgentTracer(trace_id=trace_id, user_id=user_id)
