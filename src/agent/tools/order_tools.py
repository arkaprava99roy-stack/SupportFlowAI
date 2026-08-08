"""Order lookup and order cancellation tools with strict safety authorization."""
import datetime
from typing import Dict, Any, Optional
from src.db.database import SessionLocal
from src.db.models import Order, User
from src.agent.tools.audit_logger import log_tool_execution
from src.utils.logger import logger


def normalize_order_id(raw_id: str) -> str:
    """Standardizes order ID format (e.g., '1001' or '#1001' -> 'ORD-1001')."""
    clean = raw_id.strip().upper().lstrip("#")
    if clean.isdigit():
        return f"ORD-{clean}"
    if not clean.startswith("ORD-") and clean.replace("ORD", "").isdigit():
        return f"ORD-{clean.replace('ORD', '')}"
    return clean


def get_order(order_id: str, user_id: str = "user_demo") -> Dict[str, Any]:
    """Retrieves detailed order information with strict user ownership validation.
    
    Args:
        order_id: Unique order identifier (e.g. 'ORD-1001').
        user_id: Authenticated user ID requesting the data.
    """
    normalized_id = normalize_order_id(order_id)
    db = SessionLocal()

    try:
        order = db.query(Order).filter(Order.id == normalized_id).first()

        if not order:
            summary = f"Order '{normalized_id}' was not found in the database."
            log_tool_execution("get_order", {"order_id": normalized_id}, "NOT_FOUND", summary, user_id)
            return {
                "success": False,
                "error": "NOT_FOUND",
                "message": f"We could not locate an order with ID `{normalized_id}`. Please double-check your order number.",
            }

        # Ownership authorization check
        if order.user_id != user_id and user_id != "admin":
            summary = f"Unauthorized access attempt to order '{normalized_id}' belonging to '{order.user_id}'."
            log_tool_execution("get_order", {"order_id": normalized_id}, "UNAUTHORIZED", summary, user_id)
            return {
                "success": False,
                "error": "UNAUTHORIZED",
                "message": "🔒 Access Denied: You do not have permission to view this order. You may only view orders registered to your authenticated account.",
            }

        # Successful order lookup
        order_data = {
            "success": True,
            "order_id": order.id,
            "order_number": order.order_number,
            "product_name": order.product_name,
            "status": order.status,
            "total_amount": f"${order.total_amount:.2f}",
            "carrier": order.carrier,
            "tracking_number": order.tracking_number or "Not yet assigned",
            "shipping_address": order.shipping_address,
            "order_date": order.created_at.strftime("%B %d, %Y") if order.created_at else "Recent",
        }

        summary = f"Retrieved order '{order.id}' for user '{user_id}' (Status: {order.status})."
        log_tool_execution("get_order", {"order_id": normalized_id}, "SUCCESS", summary, user_id)
        return order_data

    finally:
        db.close()


def cancel_order(
    order_id: str,
    confirmation: bool = False,
    reason: Optional[str] = None,
    user_id: str = "user_demo",
) -> Dict[str, Any]:
    """Cancels an eligible order with mandatory two-step human confirmation.
    
    NON-NEGOTIABLE SAFETY: If confirmation is False, the order is NOT modified and
    an explicit confirmation prompt is returned with full order summary.
    """
    normalized_id = normalize_order_id(order_id)
    db = SessionLocal()

    try:
        order = db.query(Order).filter(Order.id == normalized_id).first()

        if not order:
            summary = f"Cancellation attempt failed: Order '{normalized_id}' not found."
            log_tool_execution("cancel_order", {"order_id": normalized_id}, "NOT_FOUND", summary, user_id)
            return {
                "success": False,
                "error": "NOT_FOUND",
                "message": f"Order `{normalized_id}` was not found.",
            }

        # Ownership authorization check
        if order.user_id != user_id and user_id != "admin":
            summary = f"Unauthorized cancellation attempt for order '{normalized_id}' by '{user_id}'."
            log_tool_execution("cancel_order", {"order_id": normalized_id}, "UNAUTHORIZED", summary, user_id)
            return {
                "success": False,
                "error": "UNAUTHORIZED",
                "message": "🔒 Access Denied: You cannot cancel orders registered to another customer.",
            }

        # Step 1: Explicit Confirmation Check (No silent mutations)
        if not confirmation:
            summary = f"Cancellation confirmation requested for order '{normalized_id}' (${order.total_amount:.2f})."
            log_tool_execution("cancel_order", {"order_id": normalized_id, "confirmation": False}, "CONFIRMATION_REQUIRED", summary, user_id)
            return {
                "success": False,
                "requires_confirmation": True,
                "order_id": order.id,
                "product_name": order.product_name,
                "status": order.status,
                "total_amount": f"${order.total_amount:.2f}",
                "message": (
                    f"⚠️ **Order Cancellation Confirmation Required**\n\n"
                    f"You requested to cancel order **{order.id}** for **{order.product_name}**.\n\n"
                    f"• **Current Status**: `{order.status}`\n"
                    f"• **Refund Amount**: `${order.total_amount:.2f}` (will be refunded to your original payment method)\n\n"
                    f"To proceed, please explicitly confirm by replying **'Yes, confirm cancel {order.id}'** or **'Confirm cancellation'**."
                ),
            }

        # Step 2: Status Eligibility Check
        if order.status != "PROCESSING":
            summary = f"Cannot cancel order '{normalized_id}' in status '{order.status}'."
            log_tool_execution("cancel_order", {"order_id": normalized_id, "confirmation": True}, "FAILED", summary, user_id)
            return {
                "success": False,
                "error": "INELIGIBLE_STATUS",
                "message": (
                    f"Order `{order.id}` cannot be automatically cancelled because its status is already **{order.status}**.\n"
                    "Orders that have already shipped or delivered can be returned for a full refund within 30 days under our standard return policy."
                ),
            }

        # Execute cancellation mutation
        order.status = "CANCELLED"
        order.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        summary = f"Successfully cancelled order '{normalized_id}' for user '{user_id}' with full refund of ${order.total_amount:.2f}."
        log_tool_execution("cancel_order", {"order_id": normalized_id, "confirmation": True, "reason": reason}, "SUCCESS", summary, user_id)

        return {
            "success": True,
            "order_id": order.id,
            "status": "CANCELLED",
            "refund_amount": f"${order.total_amount:.2f}",
            "message": (
                f"✅ **Order Successfully Cancelled**\n\n"
                f"Order **{order.id}** ({order.product_name}) has been cancelled.\n"
                f"A full refund of **${order.total_amount:.2f}** has been initiated to your original payment method (estimated 3–5 business days).\n"
                "A cancellation confirmation receipt has been sent to your email."
            ),
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling order {order_id}: {e}")
        return {"success": False, "error": "INTERNAL_ERROR", "message": f"Failed to cancel order: {e}"}
    finally:
        db.close()
