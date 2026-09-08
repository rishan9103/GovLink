import logging
from typing import Any

from rag.generator import generate_answer
from rag.retriever import retrieve_relevant_chunks

logger = logging.getLogger(__name__)


class RAGService:
    def answer_question(self, question: str, language: str = "en") -> dict[str, Any]:
        logger.info("Starting RAG flow for question")
        relevant_chunks = retrieve_relevant_chunks(question)
        context = "\n\n".join(chunk["text"] for chunk in relevant_chunks)

        answer, sources = generate_answer(question, relevant_chunks)

        return {
            "answer": answer,
            "language": language,
            "sources": sources,
            "retrieval": {
                "documents_found": len(relevant_chunks),
            },
        }
