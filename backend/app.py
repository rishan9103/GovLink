import logging
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

from config import config
from routes import chat_bp, documents_bp, services_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_SIZE

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
    )

    app.register_blueprint(chat_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(services_bp)

    @app.get("/")
    def index():
        return jsonify({"success": True, "service": "GovAssist Backend", "status": "online"})

    @app.get("/api/health")
    def health():
        return jsonify({"success": True, "status": "healthy", "service": "GovAssist Backend"})

    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Invalid request"}}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "Resource not found"}}), 404

    @app.errorhandler(422)
    def handle_unprocessable(error):
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Validation failed"}}), 422

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.exception("Unhandled server error")
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)
