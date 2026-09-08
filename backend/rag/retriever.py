from __future__ import annotations

from typing import Any

from config import config
from rag.embeddings import EmbeddingModel
from rag.vector_store import get_vector_store


def retrieve_relevant_chunks(question: str, top_k: int | None = None, similarity_threshold: float = 0.2) -> list[dict[str, Any]]:
    if not question or not question.strip():
        return []

    top_k = top_k or config.TOP_K
    model = EmbeddingModel()
    question_embedding = model.encode(question)
    vector_store = get_vector_store()
    results = vector_store.query(question_embedding, n_results=top_k)

    relevant: list[dict[str, Any]] = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for idx, document in enumerate(documents):
        metadata = metadatas[idx] if idx < len(metadatas) else {}
        distance = distances[idx] if idx < len(distances) else None
        if distance is not None:
            similarity = max(0.0, 1.0 - float(distance))
        else:
            similarity = 1.0

        if similarity < similarity_threshold:
            continue

        relevant.append({
            "text": document,
            "source": metadata.get("source"),
            "page": metadata.get("page"),
            "category": metadata.get("category"),
            "title": metadata.get("title"),
            "department": metadata.get("department"),
            "relevance": round(similarity, 4),
        })

    return relevant
