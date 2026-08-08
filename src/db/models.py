"""Complete SQLAlchemy database schema models for SupportFlow AI."""
import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Populated via auth
    name = Column(String(120), nullable=False)
    role = Column(String(20), default="customer")  # customer, agent, admin
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(100), primary_key=True)  # e.g. conv_uuid
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), default="New Conversation")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(100), primary_key=True)
    conversation_id = Column(String(100), ForeignKey("conversations.id"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)
    risk_level = Column(String(20), default="LOW")
    citations = Column(Text, nullable=True)  # Serialized JSON list of citations
    is_escalated = Column(Boolean, default=False)
    ticket_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")


class Product(Base):
    __tablename__ = "products"

    id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    in_stock = Column(Boolean, default=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True)  # e.g. ORD-1001
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    product_name = Column(String(150), nullable=False)
    status = Column(String(30), nullable=False)  # PROCESSING, SHIPPED, DELIVERED, CANCELLED, REFUNDED
    total_amount = Column(Float, nullable=False)
    carrier = Column(String(50), default="FedEx")
    tracking_number = Column(String(100), nullable=True)
    shipping_address = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="orders")
    product = relationship("Product")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(50), primary_key=True)  # e.g. TICK-5001
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), default="OPEN")  # OPEN, PENDING_REVIEW, RESOLVED, CLOSED
    category = Column(String(50), default="GENERAL")
    assigned_to = Column(String(100), default="support_tier1")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="tickets")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(100), primary_key=True)
    conversation_id = Column(String(100), ForeignKey("conversations.id"), nullable=False, index=True)
    message_id = Column(String(100), nullable=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    rating = Column(String(20), nullable=False)  # thumbs_up, thumbs_down
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="feedback")


class PendingReview(Base):
    __tablename__ = "pending_reviews"

    id = Column(String(50), primary_key=True)
    conversation_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    ticket_id = Column(String(50), nullable=True)
    risk_level = Column(String(20), nullable=False)  # MEDIUM, HIGH
    intent = Column(String(50), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_recommended_action = Column(Text, nullable=False)
    status = Column(String(30), default="PENDING")  # PENDING, APPROVED, REJECTED, RESOLVED
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class ToolAuditLog(Base):
    __tablename__ = "tool_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=True)
    tool_name = Column(String(100), nullable=False, index=True)
    arguments = Column(Text, nullable=False)  # JSON string of arguments
    result_status = Column(String(30), nullable=False)  # SUCCESS, FAILED, CONFIRMATION_REQUIRED, REFUSED
    result_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
