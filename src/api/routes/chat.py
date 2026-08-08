"""Chat and conversation persistence routes."""
import json
import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage

from src.db.database import get_db
from src.db.models import User, Conversation, Message
from src.auth.dependencies import get_current_user
from src.agent.graph import support_flow_app
from src.api.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationSummary,
    ConversationDetailResponse,
    MessageItem,
    CitationItem,
)
from src.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Chat & Conversations"])


@router.post("/chat", response_model=ChatMessageResponse)
def send_chat_message(
    req: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Executes the LangGraph multi-agent support workflow with conversation persistence."""
    conv_id = req.conversation_id

    # 1. Retrieve or create conversation record
    conversation = None
    if conv_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conv_id,
            Conversation.user_id == current_user.id,
        ).first()

    if not conversation:
        conv_id = f"conv_{uuid.uuid4().hex[:10]}"
        # Generate initial title from first message
        title_summary = req.message[:45] + ("..." if len(req.message) > 45 else "")
        conversation = Conversation(
            id=conv_id,
            user_id=current_user.id,
            title=title_summary,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        db.add(conversation)
        db.commit()

    # 2. Persist incoming User Message
    user_msg_id = f"msg_{uuid.uuid4().hex[:10]}"
    user_msg = Message(
        id=user_msg_id,
        conversation_id=conv_id,
        sender="user",
        content=req.message,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(user_msg)
    db.commit()

    # 3. Invoke LangGraph Agent Graph
    try:
        config = {"configurable": {"thread_id": conv_id}}
        state_input = {
            "user_id": current_user.id,
            "conversation_id": conv_id,
            "messages": [HumanMessage(content=req.message)],
        }
        agent_result = support_flow_app.invoke(state_input, config=config)
    except Exception as e:
        logger.error(f"LangGraph execution exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent workflow error: {str(e)}",
        )

    # 4. Extract Agent Response & Metadata
    response_text = agent_result.get("response_text")
    if not response_text and agent_result.get("messages"):
        response_text = str(agent_result["messages"][-1].content)
    elif not response_text:
        response_text = "I have processed your request. Please let me know how else I may assist you!"

    intent = agent_result.get("intent", "GENERAL")
    intent_conf = agent_result.get("intent_confidence", 0.90)
    risk_level = agent_result.get("risk_level", "LOW")
    raw_citations = agent_result.get("citations", []) or []
    is_escalated = agent_result.get("is_escalated", False)
    ticket_id = agent_result.get("ticket_id")

    # Serialize citations to JSON string
    serialized_citations = json.dumps(raw_citations) if raw_citations else None

    # 5. Persist Assistant Response
    assistant_msg_id = f"msg_{uuid.uuid4().hex[:10]}"
    now = datetime.datetime.now(datetime.timezone.utc)
    assistant_msg = Message(
        id=assistant_msg_id,
        conversation_id=conv_id,
        sender="assistant",
        content=response_text,
        intent=intent,
        risk_level=risk_level,
        citations=serialized_citations,
        is_escalated=is_escalated,
        ticket_id=ticket_id,
        created_at=now,
    )
    db.add(assistant_msg)

    # Update conversation timestamp
    conversation.updated_at = now
    db.commit()

    # Format structured citations for schema
    formatted_citations = [
        CitationItem(
            document=c.get("document", "support_doc.md"),
            title=c.get("title", "Knowledge Base"),
            category=c.get("category", "GENERAL"),
            version=str(c.get("version", "1.0")),
            updated_at=str(c.get("updated_at", "2026-01-01")),
            chunk_id=c.get("chunk_id"),
            snippet=c.get("snippet", ""),
            score=c.get("score"),
        )
        for c in raw_citations
    ]

    return ChatMessageResponse(
        conversation_id=conv_id,
        message_id=assistant_msg_id,
        response=response_text,
        intent=intent,
        intent_confidence=intent_conf,
        risk_level=risk_level,
        citations=formatted_citations,
        is_escalated=is_escalated,
        ticket_id=ticket_id,
        created_at=now.strftime("%Y-%m-%d %H:%M:%S"),
    )


@router.post("/chat/stream")
def stream_chat_message(
    req: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Streams the LangGraph multi-agent support response token-by-token using Server-Sent Events."""
    import asyncio
    from fastapi.responses import StreamingResponse

    conv_id = req.conversation_id
    conversation = None
    if conv_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conv_id,
            Conversation.user_id == current_user.id,
        ).first()

    if not conversation:
        conv_id = f"conv_{uuid.uuid4().hex[:10]}"
        title_summary = req.message[:45] + ("..." if len(req.message) > 45 else "")
        conversation = Conversation(
            id=conv_id,
            user_id=current_user.id,
            title=title_summary,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        db.add(conversation)
        db.commit()

    # Persist User Message
    user_msg_id = f"msg_{uuid.uuid4().hex[:10]}"
    user_msg = Message(
        id=user_msg_id,
        conversation_id=conv_id,
        sender="user",
        content=req.message,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(user_msg)
    db.commit()

    # Execute LangGraph Agent
    config = {"configurable": {"thread_id": conv_id}}
    state_input = {
        "user_id": current_user.id,
        "conversation_id": conv_id,
        "messages": [HumanMessage(content=req.message)],
    }
    agent_result = support_flow_app.invoke(state_input, config=config)

    response_text = agent_result.get("response_text")
    if not response_text and agent_result.get("messages"):
        response_text = str(agent_result["messages"][-1].content)
    elif not response_text:
        response_text = "I have processed your request. Please let me know how else I may assist you!"

    intent = agent_result.get("intent", "GENERAL")
    intent_conf = agent_result.get("intent_confidence", 0.90)
    risk_level = agent_result.get("risk_level", "LOW")
    raw_citations = agent_result.get("citations", []) or []
    is_escalated = agent_result.get("is_escalated", False)
    ticket_id = agent_result.get("ticket_id")

    # Persist Assistant Message
    assistant_msg_id = f"msg_{uuid.uuid4().hex[:10]}"
    now = datetime.datetime.utcnow()
    assistant_msg = Message(
        id=assistant_msg_id,
        conversation_id=conv_id,
        sender="assistant",
        content=response_text,
        intent=intent,
        risk_level=risk_level,
        citations=json.dumps(raw_citations) if raw_citations else None,
        is_escalated=is_escalated,
        ticket_id=ticket_id,
        created_at=now,
    )
    db.add(assistant_msg)
    conversation.updated_at = now
    db.commit()

    formatted_citations = [
        {
            "document": c.get("document", "support_doc.md"),
            "title": c.get("title", "Knowledge Base"),
            "category": c.get("category", "GENERAL"),
            "version": str(c.get("version", "1.0")),
            "updated_at": str(c.get("updated_at", "2026-01-01")),
            "snippet": c.get("snippet", ""),
            "score": c.get("score"),
        }
        for c in raw_citations
    ]

    def event_generator():
        # Stream text words in chunks
        words = response_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            payload = json.dumps({"token": chunk})
            yield f"data: {payload}\n\n"

        # Emit trailing metadata
        meta_payload = json.dumps({
            "conversation_id": conv_id,
            "message_id": assistant_msg_id,
            "intent": intent,
            "intent_confidence": intent_conf,
            "risk_level": risk_level,
            "citations": formatted_citations,
            "is_escalated": is_escalated,
            "ticket_id": ticket_id,
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        })
        yield f"event: metadata\ndata: {meta_payload}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/conversations", response_model=List[ConversationSummary])
def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves all conversation threads for the authenticated customer."""
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    summaries = []
    for conv in conversations:
        last_msg = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .first()
        )
        msg_count = db.query(Message).filter(Message.conversation_id == conv.id).count()

        summaries.append(
            ConversationSummary(
                id=conv.id,
                title=conv.title or "Support Conversation",
                created_at=conv.created_at.strftime("%Y-%m-%d %H:%M:%S") if conv.created_at else "",
                updated_at=conv.updated_at.strftime("%Y-%m-%d %H:%M:%S") if conv.updated_at else "",
                last_message=last_msg.content[:60] + "..." if last_msg else None,
                message_count=msg_count,
            )
        )

    return summaries


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_details(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns complete multi-turn message history with citations and metadata."""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' was not found.",
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    message_items = []
    for m in messages:
        citations_list = []
        if m.citations:
            try:
                parsed = json.loads(m.citations)
                citations_list = [
                    CitationItem(
                        document=c.get("document", "doc.md"),
                        title=c.get("title", "Document"),
                        category=c.get("category", "GENERAL"),
                        version=str(c.get("version", "1.0")),
                        updated_at=str(c.get("updated_at", "2026-01-01")),
                        snippet=c.get("snippet", ""),
                        score=c.get("score"),
                    )
                    for c in parsed
                ]
            except Exception:
                citations_list = []

        message_items.append(
            MessageItem(
                id=m.id,
                sender=m.sender,
                content=m.content,
                intent=m.intent,
                risk_level=m.risk_level,
                citations=citations_list,
                is_escalated=m.is_escalated,
                created_at=m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
            )
        )

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title or "Support Conversation",
        created_at=conversation.created_at.strftime("%Y-%m-%d %H:%M:%S") if conversation.created_at else "",
        updated_at=conversation.updated_at.strftime("%Y-%m-%d %H:%M:%S") if conversation.updated_at else "",
        messages=message_items,
    )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a conversation history and its messages."""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' was not found.",
        )

    db.delete(conversation)
    db.commit()
    return {"success": True, "message": f"Conversation '{conversation_id}' successfully deleted."}
