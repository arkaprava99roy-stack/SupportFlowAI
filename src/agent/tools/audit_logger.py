"""Audit logging for all tool executions."""
import json
import datetime
from typing import Any, Dict, Optional
from src.db.database import SessionLocal
from src.db.models import ToolAuditLog
from src.utils.logger import logger


def log_tool_execution(
    tool_name: str,
    arguments: Dict[str, Any],
    result_status: str,
    result_summary: str,
    user_id: Optional[str] = "user_demo",
) -> None:
    """Logs every tool call into the database audit trail for compliance and admin analytics."""
    db = SessionLocal()
    try:
        clean_args = {k: v for k, v in arguments.items() if not str(k).startswith("_")}
        serialized_args = json.dumps(clean_args, default=str)

        audit_entry = ToolAuditLog(
            user_id=user_id or "anonymous",
            tool_name=tool_name,
            arguments=serialized_args,
            result_status=result_status,
            result_summary=result_summary[:500],
            created_at=datetime.datetime.utcnow(),
        )
        db.add(audit_entry)
        db.commit()
        logger.info(f"[TOOL AUDIT] {user_id} -> {tool_name}() [{result_status}] - {result_summary[:80]}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to record tool audit log: {e}")
    finally:
        db.close()


def get_recent_audit_logs(limit: int = 15) -> list[Dict[str, Any]]:
    """Retrieves recent tool audit records."""
    db = SessionLocal()
    try:
        records = db.query(ToolAuditLog).order_by(ToolAuditLog.created_at.desc()).limit(limit).all()
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "tool_name": r.tool_name,
                "arguments": r.arguments,
                "result_status": r.result_status,
                "result_summary": r.result_summary,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
            }
            for r in records
        ]
    finally:
        db.close()
