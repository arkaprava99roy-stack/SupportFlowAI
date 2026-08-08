"""Initial schema migration for SupportFlow AI

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-08-08 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users Table
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=50), nullable=False, primary_key=True),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=True, server_default="customer"),
        sa.Column("status", sa.String(length=20), nullable=True, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Products Table
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=50), nullable=False, primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("in_stock", sa.Boolean(), nullable=True, server_default=sa.text("1")),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)

    # Orders Table
    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=50), nullable=False, primary_key=True),
        sa.Column("order_number", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.String(length=50), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.String(length=50), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("product_name", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("carrier", sa.String(length=50), nullable=True, server_default="FedEx"),
        sa.Column("tracking_number", sa.String(length=100), nullable=True),
        sa.Column("shipping_address", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_orders_order_number", "orders", ["order_number"], unique=True)
    op.create_index("ix_orders_user_id", "orders", ["user_id"])

    # Conversations Table
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(length=100), nullable=False, primary_key=True),
        sa.Column("user_id", sa.String(length=50), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True, server_default="New Conversation"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])

    # Messages Table
    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=100), nullable=False, primary_key=True),
        sa.Column("conversation_id", sa.String(length=100), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("sender", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(length=50), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=True, server_default="LOW"),
        sa.Column("citations", sa.Text(), nullable=True),
        sa.Column("is_escalated", sa.Boolean(), nullable=True, server_default=sa.text("0")),
        sa.Column("ticket_id", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    # Tickets Table
    op.create_table(
        "tickets",
        sa.Column("id", sa.String(length=50), nullable=False, primary_key=True),
        sa.Column("ticket_number", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.String(length=50), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=True, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=30), nullable=True, server_default="OPEN"),
        sa.Column("category", sa.String(length=50), nullable=True, server_default="GENERAL"),
        sa.Column("assigned_to", sa.String(length=100), nullable=True, server_default="support_tier1"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_tickets_ticket_number", "tickets", ["ticket_number"], unique=True)
    op.create_index("ix_tickets_user_id", "tickets", ["user_id"])

    # Feedback Table
    op.create_table(
        "feedback",
        sa.Column("id", sa.String(length=100), nullable=False, primary_key=True),
        sa.Column("conversation_id", sa.String(length=100), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("message_id", sa.String(length=100), nullable=True),
        sa.Column("user_id", sa.String(length=50), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("rating", sa.String(length=20), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # Pending Reviews Table
    op.create_table(
        "pending_reviews",
        sa.Column("id", sa.String(length=50), nullable=False, primary_key=True),
        sa.Column("conversation_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=50), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("ticket_id", sa.String(length=50), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("intent", sa.String(length=50), nullable=False),
        sa.Column("user_message", sa.Text(), nullable=False),
        sa.Column("ai_recommended_action", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True, server_default="PENDING"),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # Tool Audit Logs Table
    op.create_table(
        "tool_audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, primary_key=True),
        sa.Column("user_id", sa.String(length=50), nullable=True),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column("arguments", sa.Text(), nullable=False),
        sa.Column("result_status", sa.String(length=30), nullable=False),
        sa.Column("result_summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("tool_audit_logs")
    op.drop_table("pending_reviews")
    op.drop_table("feedback")
    op.drop_table("tickets")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("orders")
    op.drop_table("products")
    op.drop_table("users")
