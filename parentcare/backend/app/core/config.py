import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings:
    PROJECT_NAME: str = "ParentCare"
    API_V1_STR: str = "/api"
    APP_ENV: str = os.getenv("APP_ENV", "development").strip().lower()

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
    if APP_ENV == "production" and not os.getenv("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be configured in production.")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

    # Database
    # Uses Neon/PostgreSQL when DATABASE_URL is provided.
    # Falls back to SQLite for local development.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/parentcare.db",
    )
    if APP_ENV == "production" and DATABASE_URL.startswith("sqlite"):
        raise RuntimeError("Configure DATABASE_URL for the production database.")

    # File uploads
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        str(BASE_DIR / "uploads"),
    )

    # CORS
    # Add production frontend URL using:
    # FRONTEND_URL=https://your-parentcare-frontend.vercel.app
    _default_cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.29.123:5173",
        "https://localhost:5173",
        "https://127.0.0.1:5173",
        "https://192.168.29.123:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://localhost:3000",
        "https://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    CORS_ORIGINS: list[str] = _default_cors_origins.copy()

    _frontend_url = os.getenv("FRONTEND_URL")
    if _frontend_url:
        CORS_ORIGINS.append(_frontend_url.rstrip("/"))


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)