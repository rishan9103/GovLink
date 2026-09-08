from __future__ import annotations

import re
from typing import Any


def clean_text(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = raw_text.replace("\x0c", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n +", "\n", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"\s*—\s*", " — ", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.strip()
    return text


def split_text_into_chunks(
    text: str,
    source: str,
    page: int | None = None,
    title: str | None = None,
    category: str | None = None,
    department: str | None = None,
    document_id: str | None = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[dict[str, Any]]:
    cleaned = clean_text(text)
    if not cleaned:
        return []

    paragraphs = [segment.strip() for segment in re.split(r"\n\s*\n+", cleaned) if segment.strip()]
    if not paragraphs:
        return []

    chunks: list[dict[str, Any]] = []
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) <= chunk_size:
            current = (current + "\n\n" + paragraph).strip() if current else paragraph
            continue

        if current:
            chunks.append({
                "text": current,
                "metadata": {
                    "source": source,
                    "page": page,
                    "title": title,
                    "category": category,
                    "department": department,
                    "document_id": document_id,
                },
            })

        if len(paragraph) > chunk_size:
            start = 0
            while start < len(paragraph):
                end = min(start + chunk_size, len(paragraph))
                piece = paragraph[start:end]
                chunks.append({
                    "text": piece,
                    "metadata": {
                        "source": source,
                        "page": page,
                        "title": title,
                        "category": category,
                        "department": department,
                        "document_id": document_id,
                    },
                })
                start = end - chunk_overlap if end < len(paragraph) else end
        else:
            current = paragraph

    if current:
        chunks.append({
            "text": current,
            "metadata": {
                "source": source,
                "page": page,
                "title": title,
                "category": category,
                "department": department,
                "document_id": document_id,
            },
        })

    return chunks
