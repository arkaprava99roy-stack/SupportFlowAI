"""Support ticket routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User, Ticket
from src.auth.dependencies import get_current_user
from src.agent.tools.ticket_tools import create_support_ticket
from src.api.schemas import TicketCreateRequest, TicketResponse

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_endpoint(
    req: TicketCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a new support ticket."""
    result = create_support_ticket(
        user_id=current_user.id,
        title=req.title,
        description=req.description,
        priority=req.priority,
        category=req.category,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to create support ticket."),
        )

    ticket = db.query(Ticket).filter(Ticket.id == result["ticket_id"]).first()
    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        user_id=ticket.user_id,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status,
        category=ticket.category,
        assigned_to=ticket.assigned_to,
        created_at=ticket.created_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.created_at else "",
    )


@router.get("", response_model=List[TicketResponse])
def get_user_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves all tickets submitted by the authenticated customer."""
    tickets = (
        db.query(Ticket)
        .filter(Ticket.user_id == current_user.id)
        .order_by(Ticket.created_at.desc())
        .all()
    )

    return [
        TicketResponse(
            id=t.id,
            ticket_number=t.ticket_number,
            user_id=t.user_id,
            title=t.title,
            description=t.description,
            priority=t.priority,
            status=t.status,
            category=t.category,
            assigned_to=t.assigned_to,
            created_at=t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else "",
        )
        for t in tickets
    ]
