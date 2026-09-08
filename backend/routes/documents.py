import os
from datetime import datetime
from pathlib import Path

from flask import Blueprint, jsonify, request

from config import config
from database import db
from database.models import GovernmentDocument

documents_bp = Blueprint("documents", __name__)

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "data" / "documents"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@documents_bp.post("/api/documents/upload")
def upload_document():
    if "file" not in request.files:
        return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "File is required"}}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Filename is required"}}), 400

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Only PDF files are allowed"}}), 422

    if uploaded_file.content_length and uploaded_file.content_length > config.MAX_UPLOAD_SIZE:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "File too large"}}), 422

    filename = os.path.basename(uploaded_file.filename)
    file_path = UPLOAD_DIR / filename
    uploaded_file.save(file_path)

    record = GovernmentDocument(
        title=filename,
        filename=filename,
        category="General",
        department="Uploaded",
        source_url="",
        document_type="pdf",
    )
    db.add(record)
    db.commit()

    return jsonify({"success": True, "message": "File uploaded", "filename": filename})


@documents_bp.post("/api/documents/index")
def index_documents():
    from scripts.ingest_documents import ingest_documents

    result = ingest_documents()
    return jsonify({"success": True, "message": "Indexing completed", "result": result})
