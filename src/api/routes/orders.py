"""Orders and cancellations routes with strict user isolation."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User, Order
from src.auth.dependencies import get_current_user
from src.agent.tools.order_tools import cancel_order, normalize_order_id
from src.api.schemas import OrderResponse, OrderCancelRequest, OrderCancelResponse

router = APIRouter(prefix="/api/orders", tags=["Orders & Cancellations"])


@router.get("", response_model=List[OrderResponse])
def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves all orders registered to the authenticated customer."""
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return [
        OrderResponse(
            id=o.id,
            order_number=o.order_number,
            product_id=o.product_id,
            product_name=o.product_name,
            status=o.status,
            total_amount=o.total_amount,
            carrier=o.carrier,
            tracking_number=o.tracking_number,
            shipping_address=o.shipping_address,
            created_at=o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else "",
        )
        for o in orders
    ]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves single order details with ownership verification."""
    normalized_id = normalize_order_id(order_id)
    order = db.query(Order).filter(Order.id == normalized_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{normalized_id}' was not found.",
        )

    # Ownership check
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="🔒 Access Denied: You may only view orders associated with your account.",
        )

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        product_id=order.product_id,
        product_name=order.product_name,
        status=order.status,
        total_amount=order.total_amount,
        carrier=order.carrier,
        tracking_number=order.tracking_number,
        shipping_address=order.shipping_address,
        created_at=order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "",
    )


@router.post("/{order_id}/cancel", response_model=OrderCancelResponse)
def cancel_order_endpoint(
    order_id: str,
    req: OrderCancelRequest,
    current_user: User = Depends(get_current_user),
):
    """Cancels an order with mandatory confirmation check."""
    result = cancel_order(
        order_id=order_id,
        confirmation=req.confirmation,
        reason=req.reason,
        user_id=current_user.id,
    )

    if result.get("error") == "UNAUTHORIZED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=result.get("message", "Unauthorized to cancel this order."),
        )

    if result.get("error") == "NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Order not found."),
        )

    return OrderCancelResponse(
        success=result.get("success", False),
        requires_confirmation=result.get("requires_confirmation", False),
        order_id=result.get("order_id", order_id),
        status=result.get("status"),
        refund_amount=result.get("refund_amount"),
        message=result.get("message", ""),
    )
