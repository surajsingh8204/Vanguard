from sqlalchemy import text

from backend.src.database.base import Base
from backend.src.database.session import engine

# Import all models here
from backend.src.models import User


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))

        print("\n✅ Connected Successfully!\n")
        print(result.scalar())


def create_tables():
    Base.metadata.create_all(bind=engine)

    print("\n✅ Database tables created successfully!\n")


if __name__ == "__main__":
    test_connection()
    create_tables()
