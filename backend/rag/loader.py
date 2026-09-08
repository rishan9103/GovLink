from __future__ import annotations

from pathlib import Path
from typing import Any

import fitz


class PDFLoadError(RuntimeError):
    pass


def load_pdf_document(pdf_path: str | Path, category: str | None = None, department: str | None = None) -> list[dict[str, Any]]:
    path = Path(pdf_path)
    if not path.exists():
        raise PDFLoadError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise PDFLoadError(f"Unsupported file type: {path}")

    try:
        document = fitz.open(str(path))
    except Exception as exc:  # pragma: no cover - defensive
        raise PDFLoadError(f"Unable to open PDF: {path}") from exc

    extracted_pages: list[dict[str, Any]] = []
    try:
        for page_index in range(document.page_count):
            page = document[page_index]
            page_text = page.get_text("text")
            if not page_text or not page_text.strip():
                page_text = "[No extractable text available on this page. The PDF may be scanned or image-based.]"
            cleaned_text = page_text.strip()
            extracted_pages.append(
                {
                    "source": path.name,
                    "title": path.stem,
                    "page": page_index + 1,
                    "category": category,
                    "department": department,
                    "text": cleaned_text,
                }
            )
    finally:
        document.close()

    return extracted_pages


def load_pdf_documents(directory: str | Path, category: str | None = None, department: str | None = None) -> list[dict[str, Any]]:
    directory = Path(directory)
    if not directory.exists():
        raise PDFLoadError(f"Document directory does not exist: {directory}")

    pdf_files = sorted(directory.rglob("*.pdf"))
    documents: list[dict[str, Any]] = []
    for pdf_file in pdf_files:
        documents.extend(load_pdf_document(pdf_file, category=category, department=department))
    return documents
