import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Central configuration for the ATS Analyzer app."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "ats.db")

    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB max upload size

    # Scoring weights (must sum to 1.0)
    SCORE_WEIGHTS = {
        "Keyword Match": 0.40,
        "Formatting": 0.20,
        "Experience Quality": 0.25,
        "Spelling & Grammar": 0.15,
    }

    IDEAL_WORD_COUNT_MIN = 300
    IDEAL_WORD_COUNT_MAX = 800
