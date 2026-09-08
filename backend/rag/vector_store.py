from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from config import config


class ChromaVectorStore:
    def __init__(self, collection_name: str = "govassist_documents"):
        self.persist_directory = Path(config.CHROMA_PERSIST_DIRECTORY)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, chunks: list[dict[str, Any]]) -> None:
        if not chunks:
            return

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []
        embeddings: list[list[float]] = []

        for index, chunk in enumerate(chunks):
            metadata = chunk.get("metadata", {})
            text = chunk.get("text", "").strip()
            if not text:
                continue

            source = metadata.get("source") or "unknown"
            page = metadata.get("page") or 0
            document_id = metadata.get("document_id") or f"{source}:{page}:{index}"
            unique_id = f"{document_id}:{index}"
            ids.append(unique_id)
            documents.append(text)
            metadatas.append(
                {
                    "source": source,
                    "page": page,
                    "title": metadata.get("title"),
                    "category": metadata.get("category"),
                    "department": metadata.get("department"),
                    "document_id": document_id,
                }
            )
            embeddings.append(chunk.get("embedding", []))

        if documents:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings)

    def add_texts(self, texts: list[str], metadatas: list[dict[str, Any]] | None = None, ids: list[str] | None = None) -> None:
        if metadatas is None:
            metadatas = [{} for _ in texts]
        if ids is None:
            ids = [f"doc-{index}" for index in range(len(texts))]

        self.collection.add(documents=texts, metadatas=metadatas, ids=ids)

    def query(self, query_embedding: list[float], n_results: int = 5):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

    def count(self) -> int:
        return self.collection.count()


def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore()
