from __future__ import annotations

import logging
import os
from typing import Any

from config import config
from rag.prompt import build_prompt

logger = logging.getLogger(__name__)


def generate_answer(question: str, chunks: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    if not chunks:
        return (
            "The available government documents do not provide enough information to answer this question accurately.",
            [],
        )

    if not config.LLM_API_KEY and config.LLM_PROVIDER.lower() not in {"mock", "none"}:
        raise ValueError("LLM API key is not configured. Set LLM_API_KEY in the environment or use a mock provider for testing.")

    prompt = build_prompt(question, chunks)
    logger.info("Generated prompt with %s chunk(s)", len(chunks))

    if config.LLM_PROVIDER.lower() == "mock":
        answer = "Based on the retrieved government material, the available information indicates the query is addressed in the supplied documents. Please review the cited sources for exact requirements."
        return answer, [
            {
                "title": chunk.get("title") or "Government document",
                "source": chunk.get("source") or "unknown",
                "page": chunk.get("page"),
                "category": chunk.get("category"),
            }
            for chunk in chunks
        ]

    if config.LLM_PROVIDER.lower() == "openai":
        try:
            import openai
        except ImportError as exc:  # pragma: no cover
            raise ValueError("OpenAI Python SDK is not installed. Install backend dependencies first.") from exc

        client = openai.OpenAI(api_key=config.LLM_API_KEY)
        response = client.responses.create(
            model=config.LLM_MODEL,
            input=[
                {"role": "system", "content": "You are GovAssist. Use the cited government context and do not invent facts."},
                {"role": "user", "content": prompt},
            ],
        )
        answer = response.output_text.strip() if hasattr(response, "output_text") else "Unable to generate a response."
        return answer, [
            {
                "title": chunk.get("title") or "Government document",
                "source": chunk.get("source") or "unknown",
                "page": chunk.get("page"),
                "category": chunk.get("category"),
            }
            for chunk in chunks
        ]

    return (
        "The current LLM provider is not configured. Set LLM_PROVIDER and LLM_API_KEY in the environment.",
        [],
    )
