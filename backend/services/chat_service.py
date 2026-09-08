import logging

from database import db
from database.models import GovernmentService

logger = logging.getLogger(__name__)


class ChatService:
    @staticmethod
    def process_chat(message: str, session_id: str = None, language: str = "en"):
        logger.info("Processing chat message for language=%s", language)
        try:
            from services.rag_service import RAGService

            return RAGService().answer_question(message, language=language)
        except (ImportError, ModuleNotFoundError, ValueError) as exc:
            logger.warning("RAG unavailable; using service catalog fallback: %s", exc)
            return ChatService._catalog_answer(message, language)

    @staticmethod
    def _catalog_answer(message: str, language: str):
        services = db.query(GovernmentService).filter(GovernmentService.active.is_(True)).all()
        normalized_message = message.lower().replace("?", "")
        message_terms = set(normalized_message.split())
        aliases = {
            "kisan": "pm-kisan",
            "farmer": "pm-kisan",
            "farmers": "pm-kisan",
            "ujjwala": "pm ujjwala yojana",
            "lpg": "pm ujjwala yojana",
            "loan": "vidya laxmi",
            "student": "vidya laxmi",
        }
        requested_service = next((aliases[term] for term in message_terms if term in aliases), "")
        ranked = sorted(
            services,
            key=lambda service: len(message_terms & set(service.name.lower().split())) + (service.name.lower() == requested_service),
            reverse=True,
        )
        service = ranked[0] if ranked and len(message_terms & set(ranked[0].name.lower().split())) else None
        if requested_service:
            service = next((item for item in services if item.name.lower() == requested_service), service)

        if service:
            if any(term in normalized_message for term in ("eligible", "eligibility", "qualify", "who can")):
                answer = f"{service.name} eligibility: {service.eligibility or 'See the official service guidance.'}"
            elif any(term in normalized_message for term in ("apply", "application", "how do", "register", "process")):
                answer = f"To apply for {service.name}: {service.application_process or 'Follow the official application process.'}"
            elif any(term in normalized_message for term in ("what is", "about", "provide", "offer")):
                answer = f"{service.name}: {service.description or 'Government service information is available.'}"
            else:
                answer = (
                    f"{service.name}: {service.description or 'Government service information is available.'} "
                    f"Eligibility: {service.eligibility or 'See the official service guidance.'} "
                    f"Application: {service.application_process or 'Follow the official application process.'}"
                )
            sources = [{"title": service.name, "source": service.official_url or "Service catalog", "category": service.category.name if service.category else None}]
        else:
            names = ", ".join(service.name for service in services)
            answer = f"I can help with these services: {names}. Ask about a specific service to see eligibility and application guidance."
            sources = [{"title": "GovAssist service catalog", "source": "Service catalog"}]

        return {"answer": answer, "language": language, "sources": sources, "retrieval": {"documents_found": 0, "catalog_fallback": True}}
