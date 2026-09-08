from sqlalchemy import select

from .connection import db
from .models import Category, GovernmentService


def seed_categories():
    categories = [
        {"name": "Agriculture", "description": "Agricultural schemes and assistance"},
        {"name": "Education", "description": "Scholarships and educational support"},
        {"name": "Welfare", "description": "Social welfare schemes"},
        {"name": "Employment", "description": "Employment and skill schemes"},
        {"name": "Scholarships", "description": "Scholarship and study assistance"},
        {"name": "Subsidies", "description": "Subsidy and benefit programs"},
    ]

    existing = db.query(Category).count()
    if existing > 0:
        return

    for item in categories:
        db.add(Category(**item))
    db.commit()


def seed_services():
    if db.query(GovernmentService).count() > 0:
        return

    agriculture = db.query(Category).filter(Category.name == "Agriculture").first()
    education = db.query(Category).filter(Category.name == "Education").first()
    welfare = db.query(Category).filter(Category.name == "Welfare").first()

    sample_services = [
        GovernmentService(
            name="PM-KISAN",
            category_id=agriculture.id,
            description="Pradhan Mantri Kisan Samman Nidhi supports eligible farmer families with income support.",
            eligibility="Small and marginal farmer families as defined by the scheme guidelines.",
            application_process="Register through the official portal or local agriculture office and complete the verification steps.",
            official_url="https://pmkisan.gov.in/",
            active=True,
        ),
        GovernmentService(
            name="Vidya Laxmi",
            category_id=education.id,
            description="Education loan portal for students seeking support for higher education.",
            eligibility="Indian students pursuing higher education and meeting the bank and scheme requirements.",
            application_process="Apply online through the portal with required academic and personal details.",
            official_url="https://www.vidyalakshmi.co.in/",
            active=True,
        ),
        GovernmentService(
            name="PM Ujjwala Yojana",
            category_id=welfare.id,
            description="Support for LPG connections and cleaner cooking fuel access.",
            eligibility="Eligible households as defined by the scheme criteria.",
            application_process="Apply through the designated official process with required household documents.",
            official_url="https://www.pmuy.gov.in/",
            active=True,
        ),
    ]

    db.add_all(sample_services)
    db.commit()


def seed_database():
    seed_categories()
    seed_services()
