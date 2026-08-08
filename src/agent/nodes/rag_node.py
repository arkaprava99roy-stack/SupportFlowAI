"""RAG node: queries FAISS vector index and builds citation structures."""
from typing import Dict, Any, List
from src.agent.state import AgentState
from src.agent.nodes.intent_classifier import get_latest_user_message
from src.rag.retriever import retrieve_relevant_documents
from src.utils.logger import logger


def rag_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node: searches knowledge base for context and prepares citations."""
    user_message = get_latest_user_message(state.get("messages", []))
    intent = state.get("intent", "GENERAL")

    logger.info(f"RAG Node searching knowledge base for: '{user_message}' (intent: {intent})")

    # Map intent to knowledge base category if applicable
    category_filter = None
    if intent in ["BILLING", "REFUND", "SHIPPING", "ACCOUNT", "SECURITY"]:
        category_filter = intent

    docs, citations = retrieve_relevant_documents(
        query=user_message,
        top_k=5,
        category_filter=None,  # Do broad search with semantic similarity
    )

    serialized_docs: List[Dict[str, Any]] = []
    for doc in docs:
        serialized_docs.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
        })

    logger.info(f"RAG Node retrieved {len(serialized_docs)} chunks and {len(citations)} citations")

    return {
        "retrieved_docs": serialized_docs,
        "citations": citations,
    }
