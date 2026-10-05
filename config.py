"""Environment-driven application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    APP_ENV = os.getenv("APP_ENV", "development")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db").replace(
        "postgres://", "postgresql://", 1
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10485760"))
    MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "300"))
    MAX_EXTRACTED_CHARACTERS = int(os.getenv("MAX_EXTRACTED_CHARACTERS", "2000000"))
    UPLOAD_FOLDER = str(ROOT / "uploads")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = APP_ENV == "production"
    REMEMBER_COOKIE_SECURE = APP_ENV == "production"
    MAX_FORM_PARTS = 30
