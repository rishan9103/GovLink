from .connection import Base, engine
from .models import *  # noqa: F401,F403
from .seed import seed_database


def initialize_database():
    Base.metadata.create_all(bind=engine)
    seed_database()
    return True


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
