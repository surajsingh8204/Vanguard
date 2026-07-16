import os
from pathlib import Path

from dotenv import load_dotenv

# backend/
BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


class Settings:
    """
    Backend application settings.
    """

    # ------------------------
    # FastAPI
    # ------------------------
    APP_NAME = os.getenv("APP_NAME", "Vanguard Backend")
    APP_VERSION = os.getenv("APP_VERSION", "0.6.0")
    APP_DESCRIPTION = os.getenv(
        "APP_DESCRIPTION",
        "Predictive Narrative Intelligence Platform"
    )

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))

    # ------------------------
    # Database
    # ------------------------
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # ------------------------
    # Security
    # ------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )

    # ------------------------
    # Intelligence Engine
    # ------------------------
    INTELLIGENCE_PATH = os.getenv(
        "INTELLIGENCE_PATH",
        "../intelligence"
    )


settings = Settings()
