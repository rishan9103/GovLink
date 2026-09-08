import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATABASE_URL", "sqlite:///test_govassist.db")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("LLM_API_KEY", "")
os.environ.setdefault("CHROMA_PERSIST_DIRECTORY", str(Path(__file__).resolve().parents[1] / "chroma_db_test"))

import pytest
from app import create_app
from database.connection import Base, engine
from database.models import *  # noqa: F401,F403


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    Base.metadata.drop_all(bind=engine)
