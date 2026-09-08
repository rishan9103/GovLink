from database import db
from database.models import Category, GovernmentService


class ServiceCatalog:
    @staticmethod
    def get_services(category: str | None = None):
        query = db.query(GovernmentService).filter(GovernmentService.active.is_(True))
        if category:
            query = query.join(Category).filter(Category.name.ilike(category))
        return query.order_by(GovernmentService.name).all()

    @staticmethod
    def get_categories():
        return db.query(Category).order_by(Category.name).all()
