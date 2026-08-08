"""Knowledge base document ingestion and FAISS vector index builder."""
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

from src.config import settings
from src.utils.logger import logger


class FallbackEmbeddings(Embeddings):
    """Deterministic, lightweight embedding model for testing and offline environments.
    
    Generates a normalized 384-dimensional dense representation using bag-of-words
    and character n-gram hashing via CRC32.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _embed_text(self, text: str) -> List[float]:
        import zlib
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vec.tolist()

        for word in words:
            # Deterministic word hash
            h_w = zlib.crc32(word.encode("utf-8")) % self.dimension
            vec[h_w] += 1.0
            # Character bigram hashes
            for i in range(len(word) - 1):
                bg = word[i : i + 2]
                h_bg = zlib.crc32(bg.encode("utf-8")) % self.dimension
                vec[h_bg] += 0.5

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text)


def get_embedding_model() -> Embeddings:
    """Returns OpenAIEmbeddings if an API key is configured; otherwise returns FallbackEmbeddings."""
    if settings.has_valid_api_key:
        try:
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL_NAME,
                api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"),
            )
        except Exception as exc:
            logger.warning(f"Failed to initialize OpenAIEmbeddings ({exc}). Using fallback embeddings.")
            return FallbackEmbeddings()
    return FallbackEmbeddings()


def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Extracts frontmatter YAML key-values and raw markdown body from document."""
    metadata: Dict[str, Any] = {}
    body = content

    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if frontmatter_match:
        fm_text, body = frontmatter_match.groups()
        for line in fm_text.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip()] = val.strip().strip('"').strip("'")

    # If title not found in frontmatter, extract first heading
    if "title" not in metadata:
        heading_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if heading_match:
            metadata["title"] = heading_match.group(1).strip()
        else:
            metadata["title"] = "Knowledge Base Document"

    return metadata, body


def load_knowledge_base_docs(kb_dir: Optional[Path] = None) -> List[Document]:
    """Scans and parses all markdown files in the knowledge base directory."""
    directory = kb_dir or settings.KNOWLEDGE_BASE_DIR
    if not directory.exists():
        raise FileNotFoundError(f"Knowledge base directory not found at {directory}")

    md_files = list(directory.glob("*.md"))
    if not md_files:
        raise ValueError(f"No markdown documents found in {directory}")

    documents: List[Document] = []
    for file_path in md_files:
        try:
            raw_text = file_path.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(raw_text)

            meta.setdefault("document", file_path.name)
            meta.setdefault("source", str(file_path))
            meta.setdefault("category", meta.get("category", "GENERAL").upper())
            meta.setdefault("version", meta.get("version", "1.0"))
            meta.setdefault("updated_at", meta.get("updated_at", "2026-01-01"))

            doc = Document(page_content=body.strip(), metadata=meta)
            documents.append(doc)
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")

    logger.info(f"Loaded {len(documents)} knowledge base documents from {directory}")
    return documents


def chunk_documents(documents: List[Document]) -> List[Document]:
    """Splits knowledge base documents into chunks and tags each with rich metadata."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
        keep_separator=True,
    )

    chunks: List[Document] = []
    for doc_idx, doc in enumerate(documents):
        split_docs = text_splitter.split_documents([doc])
        for chunk_idx, chunk in enumerate(split_docs):
            chunk.metadata = {
                **doc.metadata,
                "chunk_id": f"{doc.metadata.get('document', f'doc_{doc_idx}')}#chunk_{chunk_idx}",
                "chunk_index": chunk_idx,
                "total_chunks": len(split_docs),
            }
            chunks.append(chunk)

    logger.info(f"Split {len(documents)} documents into {len(chunks)} searchable chunks")
    return chunks


def ingest_documents(
    kb_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
) -> FAISS:
    """End-to-end ingestion pipeline: load -> clean -> chunk -> embed -> FAISS index."""
    kb_directory = kb_dir or settings.KNOWLEDGE_BASE_DIR
    index_directory = output_dir or settings.FAISS_INDEX_DIR

    docs = load_knowledge_base_docs(kb_directory)
    chunks = chunk_documents(docs)

    embedding_model = get_embedding_model()
    logger.info(f"Creating FAISS vector index using {embedding_model.__class__.__name__}...")

    vector_store = FAISS.from_documents(chunks, embedding_model)

    index_directory.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(index_directory))
    logger.info(f"Successfully saved FAISS index with {len(chunks)} chunks to {index_directory}")

    return vector_store


if __name__ == "__main__":
    print("Running SupportFlow AI Knowledge Base Ingestion...")
    ingest_documents()
    print("Ingestion complete.")
