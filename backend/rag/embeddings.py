from __future__ import annotations

from functools import lru_cache
from typing import Any

from sentence_transformers import SentenceTransformer

from config import config


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(config.EMBEDDING_MODEL)


class EmbeddingModel:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or config.EMBEDDING_MODEL
        self.model = get_embedding_model()

    def encode(self, text: str | list[str]) -> list[list[float]] | list[float]:
        if isinstance(text, str):
            vector = self.model.encode(text, normalize_embeddings=True)
            return vector.tolist() if hasattr(vector, "tolist") else list(vector)
        embeddings = self.model.encode(text, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist() if hasattr(embeddings, "tolist") else list(embeddings)
