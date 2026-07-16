from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.src.config.settings import settings

# SQLAlchemy Engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,          # Change to True if you want SQL logs
    future=True
)

# Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
