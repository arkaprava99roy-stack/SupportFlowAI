"""Pydantic v2 schemas for all FastAPI request and response payloads."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# ==========================================
# Authentication Schemas
# ==========================================
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Password must be at least 6 characters")
    name: str = Field(min_length=2, max_length=120)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    name: str
    role: str


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    status: str
    created_at: Optional[datetime] = None


# ==========================================
# Chat & Conversation Schemas
# ==========================================
class CitationItem(BaseModel):
    document: str
    title: str
    category: str
    version: str
    updated_at: str
    chunk_id: Optional[str] = None
    snippet: str
    score: Optional[float] = None


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000, description="Customer message")
    conversation_id: Optional[str] = Field(default=None, description="Existing conversation thread ID to resume")


class ChatMessageResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    intent: Optional[str] = "GENERAL"
    intent_confidence: Optional[float] = 0.9
    risk_level: Optional[str] = "LOW"
    citations: List[CitationItem] = []
    is_escalated: bool = False
    ticket_id: Optional[str] = None
    created_at: str


class MessageItem(BaseModel):
    id: str
    sender: str  # user, assistant
    content: str
    intent: Optional[str] = None
    risk_level: Optional[str] = None
    citations: List[CitationItem] = []
    is_escalated: bool = False
    created_at: str


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    last_message: Optional[str] = None
    message_count: int = 0


class ConversationDetailResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[MessageItem] = []


# ==========================================
# Order Schemas
# ==========================================
class OrderResponse(BaseModel):
    id: str
    order_number: str
    product_id: str
    product_name: str
    status: str
    total_amount: float
    carrier: Optional[str] = "FedEx"
    tracking_number: Optional[str] = None
    shipping_address: str
    created_at: str


class OrderCancelRequest(BaseModel):
    confirmation: bool = Field(default=False, description="Explicit confirmation boolean")
    reason: Optional[str] = Field(default="Customer requested cancellation")


class OrderCancelResponse(BaseModel):
    success: bool
    requires_confirmation: Optional[bool] = False
    order_id: str
    status: Optional[str] = None
    refund_amount: Optional[str] = None
    message: str


# ==========================================
# Ticket Schemas
# ==========================================
class TicketCreateRequest(BaseModel):
    title: str = Field(min_length=4, max_length=200)
    description: str = Field(min_length=10)
    priority: str = Field(default="MEDIUM")
    category: str = Field(default="GENERAL")


class TicketResponse(BaseModel):
    id: str
    ticket_number: str
    user_id: str
    title: str
    description: str
    priority: str
    status: str
    category: str
    assigned_to: str
    created_at: str


# ==========================================
# Feedback Schemas
# ==========================================
class FeedbackCreateRequest(BaseModel):
    conversation_id: str
    message_id: Optional[str] = None
    rating: str = Field(description="thumbs_up or thumbs_down")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    success: bool
    feedback_id: str
    message: str
