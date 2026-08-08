"""Support ticket creation and human-in-the-loop escalation queue tools."""
import uuid
import datetime
from typing import Dict, Any, Optional, List
from src.db.database import SessionLocal
from src.db.models import Ticket, PendingReview, User
from src.agent.tools.audit_logger import log_tool_execution
from src.utils.logger import logger


def create_support_ticket(
    user_id: str,
    title: str,
    description: str,
    priority: str = "MEDIUM",
    category: str = "GENERAL",
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a formal support ticket and assigns it to the support team.
    
    Args:
        user_id: Customer ID.
        title: Summary of the issue.
        description: Full context or customer query.
        priority: LOW, MEDIUM, HIGH, or CRITICAL.
        category: Support category.
        conversation_id: Optional thread ID.
    """
    db = SessionLocal()
    try:
        # Generate ticket identifier
        count = db.query(Ticket).count()
        ticket_id = f"TICK-{5000 + count + 1}"

        ticket = Ticket(
            id=ticket_id,
            ticket_number=ticket_id,
            user_id=user_id,
            title=title,
            description=description,
            priority=priority.upper(),
            status="OPEN" if priority != "HIGH" else "PENDING_REVIEW",
            category=category.upper(),
            assigned_to="security_team" if category == "SECURITY" else "support_tier1",
            created_at=datetime.datetime.utcnow(),
        )
        db.add(ticket)
        db.commit()

        # If HIGH risk/priority, auto-enqueue for human review
        if priority.upper() in ("HIGH", "CRITICAL"):
            review_id = f"REV-{uuid.uuid4().hex[:6].upper()}"
            review = PendingReview(
                id=review_id,
                conversation_id=conversation_id or "session_direct",
                user_id=user_id,
                ticket_id=ticket_id,
                risk_level="HIGH",
                intent=category.upper(),
                user_message=description,
                ai_recommended_action="Emergency account review: verify unauthorized access, reset auth credentials, initiate owner verification.",
                status="PENDING",
                created_at=datetime.datetime.utcnow(),
            )
            db.add(review)
            db.commit()

        summary = f"Created support ticket '{ticket_id}' ({priority}) for user '{user_id}'."
        log_tool_execution("create_support_ticket", {"title": title, "priority": priority, "category": category}, "SUCCESS", summary, user_id)

        return {
            "success": True,
            "ticket_id": ticket_id,
            "priority": priority.upper(),
            "category": category.upper(),
            "assigned_to": ticket.assigned_to,
            "created_at": ticket.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Support Ticket **{ticket_id}** has been registered with priority **{priority.upper()}**.",
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating ticket: {e}")
        return {"success": False, "error": str(e), "message": "Failed to create support ticket."}
    finally:
        db.close()


def enqueue_pending_review(
    user_id: str,
    conversation_id: str,
    intent: str,
    risk_level: str,
    user_message: str,
    ai_recommended_action: str,
    ticket_id: Optional[str] = None,
) -> str:
    """Enqueues an escalated or flagged conversation for human supervisor review."""
    db = SessionLocal()
    try:
        review_id = f"REV-{uuid.uuid4().hex[:6].upper()}"
        review = PendingReview(
            id=review_id,
            conversation_id=conversation_id,
            user_id=user_id,
            ticket_id=ticket_id,
            risk_level=risk_level.upper(),
            intent=intent.upper(),
            user_message=user_message,
            ai_recommended_action=ai_recommended_action,
            status="PENDING",
            created_at=datetime.datetime.utcnow(),
        )
        db.add(review)
        db.commit()
        logger.info(f"Enqueued conversation '{conversation_id}' to pending reviews (ID: {review_id})")
        return review_id
    except Exception as e:
        db.rollback()
        logger.error(f"Error enqueueing pending review: {e}")
        return ""
    finally:
        db.close()


def get_pending_reviews(status_filter: str = "PENDING") -> List[Dict[str, Any]]:
    """Retrieves all escalated interactions waiting in the human-in-the-loop review queue."""
    db = SessionLocal()
    try:
        query = db.query(PendingReview)
        if status_filter:
            query = query.filter(PendingReview.status == status_filter.upper())
        reviews = query.order_by(PendingReview.created_at.desc()).all()

        return [
            {
                "id": r.id,
                "conversation_id": r.conversation_id,
                "user_id": r.user_id,
                "ticket_id": r.ticket_id or "N/A",
                "risk_level": r.risk_level,
                "intent": r.intent,
                "user_message": r.user_message,
                "ai_recommended_action": r.ai_recommended_action,
                "status": r.status,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
            }
            for r in reviews
        ]
    finally:
        db.close()
