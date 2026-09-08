from flask import Blueprint, jsonify, request

from database import db
from database.models import Category, GovernmentService

services_bp = Blueprint("services", __name__)


@services_bp.get("/api/services")
@services_bp.get("/api/services/")
def list_services():
    category_name = request.args.get("category")
    query = db.query(GovernmentService).join(Category).filter(GovernmentService.active.is_(True))

    if category_name:
        query = query.filter(Category.name.ilike(category_name))

    services = query.order_by(GovernmentService.name).all()
    return jsonify({
        "success": True,
        "services": [
            {
                "id": service.id,
                "name": service.name,
                "category": service.category.name if service.category else None,
                "description": service.description,
                "eligibility": service.eligibility,
                "application_process": service.application_process,
                "official_url": service.official_url,
            }
            for service in services
        ],
    })


@services_bp.get("/api/categories")
def list_categories():
    categories = db.query(Category).order_by(Category.name).all()
    return jsonify({
        "success": True,
        "categories": [
            {"id": category.id, "name": category.name, "description": category.description}
            for category in categories
        ],
    })
