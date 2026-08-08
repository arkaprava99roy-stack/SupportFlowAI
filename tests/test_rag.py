"""Tests for RAG ingestion, vector storage, and retrieval."""
import pytest
from pathlib import Path
from langchain_core.documents import Document

from src.rag.ingest import (
    load_knowledge_base_docs,
    chunk_documents,
    parse_frontmatter,
    ingest_documents,
    FallbackEmbeddings,
)
from src.rag.retriever import retrieve_relevant_documents, format_citation
from src.config import settings


def test_parse_frontmatter():
    """Verify frontmatter parsing extracts YAML metadata and body correctly."""
    sample_text = """---
title: Test Document Title
category: BILLING
version: "3.0"
updated_at: "2026-08-01"
---

# Heading
This is the document body text."""

    meta, body = parse_frontmatter(sample_text)
    assert meta["title"] == "Test Document Title"
    assert meta["category"] == "BILLING"
    assert meta["version"] == "3.0"
    assert "This is the document body text." in body


def test_load_knowledge_base_docs():
    """Verify all knowledge base markdown documents are loaded with required metadata."""
    docs = load_knowledge_base_docs(settings.KNOWLEDGE_BASE_DIR)
    assert len(docs) >= 5

    categories = {doc.metadata.get("category") for doc in docs}
    assert "REFUND" in categories
    assert "BILLING" in categories
    assert "SHIPPING" in categories
    assert "SECURITY" in categories

    for doc in docs:
        assert "document" in doc.metadata
        assert "version" in doc.metadata
        assert "title" in doc.metadata
        assert len(doc.page_content) > 50


def test_chunk_documents():
    """Verify chunking splits documents and preserves rich metadata."""
    docs = load_knowledge_base_docs(settings.KNOWLEDGE_BASE_DIR)
    chunks = chunk_documents(docs)
    assert len(chunks) >= len(docs)

    for chunk in chunks:
        assert "chunk_id" in chunk.metadata
        assert "chunk_index" in chunk.metadata
        assert "document" in chunk.metadata
        assert "category" in chunk.metadata


def test_fallback_embeddings():
    """Verify fallback deterministic embeddings generate correct dimensions."""
    emb = FallbackEmbeddings(dimension=384)
    vec = emb.embed_query("What is the refund policy?")
    assert len(vec) == 384
    assert any(v != 0 for v in vec)


def test_ingest_and_retrieval(tmp_path: Path):
    """Verify full ingestion to FAISS and similarity retrieval."""
    vector_store = ingest_documents(
        kb_dir=settings.KNOWLEDGE_BASE_DIR,
        output_dir=tmp_path,
    )
    assert vector_store is not None

    docs, citations = retrieve_relevant_documents(
        query="What is the 30-day refund guarantee window?",
        top_k=2,
        index_dir=tmp_path,
    )
    assert len(docs) > 0
    assert len(citations) == len(docs)

    top_citation = citations[0]
    assert "document" in top_citation
    assert "category" in top_citation
    assert "version" in top_citation
    assert "snippet" in top_citation
