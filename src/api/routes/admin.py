"""Admin analytics, human review queue, and audit log endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User, Conversation, Message, Ticket, PendingReview, Order
from src.auth.dependencies import get_current_user
from src.agent.tools.ticket_tools import get_pending_reviews
from src.agent.tools.audit_logger import get_recent_audit_logs

router = APIRouter(prefix="/api/admin", tags=["Admin & Analytics"])


@router.get("/pending-reviews")
def list_pending_reviews(
    current_user: User = Depends(get_current_user),
):
    """Returns all escalated sessions waiting in the human-in-the-loop review queue."""
    return get_pending_reviews()


@router.get("/audit-logs")
def list_audit_logs(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    """Returns recent tool execution audit trail records."""
    return get_recent_audit_logs(limit=limit)


@router.get("/analytics")
def get_admin_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aggregates key support platform metrics for the admin dashboard."""
    total_convs = db.query(Conversation).count()
    total_messages = db.query(Message).count()
    total_tickets = db.query(Ticket).count()
    escalated_convs = db.query(Message).filter(Message.is_escalated == True).count()
    pending_reviews_count = db.query(PendingReview).filter(PendingReview.status == "PENDING").count()

    auto_resolved_pct = (
        round(((total_convs - pending_reviews_count) / total_convs * 100), 1)
        if total_convs > 0
        else 100.0
    )

    return {
        "total_conversations": total_convs,
        "total_messages": total_messages,
        "total_tickets": total_tickets,
        "escalated_messages": escalated_convs,
        "pending_human_reviews": pending_reviews_count,
        "auto_resolution_rate_percent": auto_resolved_pct,
    }
