from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import config
from rag.embeddings import EmbeddingModel
from rag.loader import load_pdf_document
from rag.splitter import split_text_into_chunks
from rag.vector_store import ChromaVectorStore


def compute_document_id(source: str, page: int | None, chunk_index: int) -> str:
    raw = f"{source}:{page}:{chunk_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def ingest_documents() -> dict:
    document_root = Path(__file__).resolve().parents[1] / "data" / "documents"
    pdf_files = sorted(document_root.rglob("*.pdf"))
    if not pdf_files:
        return {"success": True, "files_found": 0, "chunks_created": 0, "stored": 0}

    vector_store = ChromaVectorStore()
    embedding_model = EmbeddingModel()
    total_chunks = 0

    for pdf_path in pdf_files:
        category = pdf_path.parent.name if pdf_path.parent.name in {"agriculture", "education", "welfare", "employment", "subsidies"} else "general"
        department = "Government"
        pages = load_pdf_document(pdf_path, category=category, department=department)
        for page_data in pages:
            chunks = split_text_into_chunks(
                text=page_data["text"],
                source=page_data["source"],
                page=page_data["page"],
                title=page_data["title"],
                category=category,
                department=department,
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP,
            )
            if not chunks:
                continue

            for idx, chunk in enumerate(chunks):
                text = chunk["text"]
                embedding = embedding_model.encode(text)
                chunk["embedding"] = embedding
                chunk["metadata"]["document_id"] = compute_document_id(page_data["source"], page_data["page"], idx)

            total_chunks += len(chunks)
            vector_store.add_documents(chunks)

    return {
        "success": True,
        "files_found": len(pdf_files),
        "chunks_created": total_chunks,
        "stored": vector_store.count(),
    }


if __name__ == "__main__":
    result = ingest_documents()
    print(f"Found {result['files_found']} PDF files")
    print(f"Chunks created: {result['chunks_created']}")
    print(f"Stored in ChromaDB: {result['stored']}")
    print("Completed successfully.")
