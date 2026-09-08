import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.connection import Base, engine
from database.models import *  # noqa: F401,F403
from database.seed import seed_database


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_database()
    print("Database initialized successfully.")
