import logging
import uuid

from flask import Blueprint, jsonify, request

from config import config
from database import db
from database.models import ChatMessage, ChatSession

chat_bp = Blueprint("chat", __name__)
logger = logging.getLogger(__name__)


@chat_bp.post("/api/chat")
def chat():
    from services.chat_service import ChatService

    if not request.is_json:
        return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "JSON body required"}}), 400

    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "").strip()
    language = (payload.get("language") or "en").lower()
    session_id = payload.get("session_id") or str(uuid.uuid4())

    if not message:
        return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Message is required"}}), 400

    if len(message) > config.MAX_MESSAGE_LENGTH:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Message too long"}}), 422

    valid_languages = {"en", "ml", "hi", "ta", "te", "kn"}
    if language not in valid_languages:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Unsupported language"}}), 422

    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if session is None:
        session = ChatSession(session_id=session_id)
        db.add(session)
        db.commit()

    logger.info("Chat request received for session %s", session_id)

    try:
        response = ChatService.process_chat(message, session_id=session_id, language=language)
    except ValueError as exc:
        return jsonify({"success": False, "error": {"code": "DEPENDENCY_ERROR", "message": str(exc)}}), 503
    except Exception as exc:  # pragma: no cover
        logger.exception("Chat processing failed")
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Unable to process request"}}), 500

    db.add(ChatMessage(session_id=session_id, role="user", message=message, language=language))
    db.add(ChatMessage(session_id=session_id, role="assistant", message=response["answer"], language=language))
    db.commit()

    return jsonify({
        "success": True,
        "answer": response["answer"],
        "language": language,
        "sources": response.get("sources", []),
        "retrieval": response.get("retrieval", {})
    })
