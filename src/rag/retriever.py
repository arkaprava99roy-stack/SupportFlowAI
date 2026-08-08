"""Retrieval interface with similarity search, metadata filtering, and citation formatting."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from src.config import settings
from src.rag.ingest import get_embedding_model, ingest_documents
from src.utils.logger import logger

_vector_store_instance: Optional[FAISS] = None


def get_vector_store(index_dir: Optional[Path] = None) -> FAISS:
    """Loads the local FAISS index or creates it if missing."""
    global _vector_store_instance

    directory = index_dir or settings.FAISS_INDEX_DIR
    index_file = directory / "index.faiss"

    if index_dir is not None and index_dir != settings.FAISS_INDEX_DIR:
        # Explicit custom directory (e.g. in tests)
        embedding_model = get_embedding_model()
        return FAISS.load_local(
            str(directory),
            embedding_model,
            allow_dangerous_deserialization=True,
        )

    if _vector_store_instance is not None:
        return _vector_store_instance

    if not index_file.exists():
        logger.info(f"FAISS index not found at {directory}. Running initial ingestion...")
        _vector_store_instance = ingest_documents(output_dir=directory)
    else:
        embedding_model = get_embedding_model()
        logger.info(f"Loading FAISS index from {directory} using {embedding_model.__class__.__name__}...")
        _vector_store_instance = FAISS.load_local(
            str(directory),
            embedding_model,
            allow_dangerous_deserialization=True,
        )

    return _vector_store_instance


def get_retriever(
    k: Optional[int] = None,
    category_filter: Optional[str] = None,
    index_dir: Optional[Path] = None,
):
    """Returns a LangChain retriever configured with top-k and optional search kwargs."""
    vector_store = get_vector_store(index_dir)
    top_k = k or settings.TOP_K_RETRIEVAL
    search_kwargs: Dict[str, Any] = {"k": top_k}

    if category_filter:
        search_kwargs["filter"] = {"category": category_filter.upper()}

    return vector_store.as_retriever(search_kwargs=search_kwargs)


def format_citation(doc: Document, score: Optional[float] = None) -> Dict[str, Any]:
    """Formats document metadata and snippet into a structured citation dictionary."""
    content = doc.page_content.strip()
    snippet = content[:200] + "..." if len(content) > 200 else content

    return {
        "document": doc.metadata.get("document", "knowledge_base.md"),
        "title": doc.metadata.get("title", "Support Knowledge Base"),
        "category": doc.metadata.get("category", "GENERAL"),
        "version": doc.metadata.get("version", "1.0"),
        "updated_at": doc.metadata.get("updated_at", "2026-01-01"),
        "chunk_id": doc.metadata.get("chunk_id", "chunk_0"),
        "snippet": snippet,
        "score": round(float(score), 4) if score is not None else None,
    }


def retrieve_relevant_documents(
    query: str,
    top_k: Optional[int] = None,
    category_filter: Optional[str] = None,
    index_dir: Optional[Path] = None,
) -> tuple[List[Document], List[Dict[str, Any]]]:
    """Performs similarity search with relevance scoring and returns raw docs + structured citations."""
    vector_store = get_vector_store(index_dir)
    k = top_k or settings.TOP_K_RETRIEVAL

    # Similarity search with score (L2 distance or inner product)
    try:
        results = vector_store.similarity_search_with_score(query, k=k)
    except Exception as e:
        logger.warning(f"similarity_search_with_score failed ({e}), falling back to similarity_search")
        raw_docs = vector_store.similarity_search(query, k=k)
        results = [(doc, 0.85) for doc in raw_docs]

    matched_docs: List[Document] = []
    citations: List[Dict[str, Any]] = []

    for doc, score in results:
        # Filter by category if requested
        if category_filter and doc.metadata.get("category") != category_filter.upper():
            continue

        matched_docs.append(doc)
        citations.append(format_citation(doc, score))

    logger.debug(f"Retrieved {len(matched_docs)} documents for query: '{query}'")
    return matched_docs, citations
