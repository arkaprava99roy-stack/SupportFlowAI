"""Customer feedback routes (thumbs up / thumbs down)."""
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User, Feedback, Conversation
from src.auth.dependencies import get_current_user
from src.api.schemas import FeedbackCreateRequest, FeedbackResponse
from src.utils.logger import logger

router = APIRouter(prefix="/api/feedback", tags=["Customer Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    req: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submits thumbs up / thumbs down feedback on an AI response."""
    feedback_id = f"fb_{uuid.uuid4().hex[:10]}"

    feedback_record = Feedback(
        id=feedback_id,
        conversation_id=req.conversation_id,
        message_id=req.message_id,
        user_id=current_user.id,
        rating=req.rating.lower(),
        comment=req.comment,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(feedback_record)
    db.commit()

    logger.info(f"Feedback recorded: {req.rating} for user '{current_user.id}' (Conv: {req.conversation_id})")

    return FeedbackResponse(
        success=True,
        feedback_id=feedback_id,
        message="Thank you for your feedback! Your ratings help SupportFlow AI improve continuously.",
    )


@router.get("/summary")
def get_feedback_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns overall feedback analytics and customer satisfaction metrics."""
    total = db.query(Feedback).count()
    thumbs_up = db.query(Feedback).filter(Feedback.rating == "thumbs_up").count()
    thumbs_down = db.query(Feedback).filter(Feedback.rating == "thumbs_down").count()

    satisfaction_rate = round((thumbs_up / total * 100), 1) if total > 0 else 100.0

    return {
        "total_feedback": total,
        "thumbs_up": thumbs_up,
        "thumbs_down": thumbs_down,
        "satisfaction_rate_percent": satisfaction_rate,
    }
