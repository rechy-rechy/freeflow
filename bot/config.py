import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CANVAS_API_URL = os.getenv("CANVAS_API_URL", "")
    CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN", "")
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    SCHOOL_EMAIL = os.getenv("SCHOOL_EMAIL", "")

    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is not set")
        if not cls.CANVAS_API_URL:
            errors.append("CANVAS_API_URL is not set")
        if not cls.CANVAS_API_TOKEN:
            errors.append("CANVAS_API_TOKEN is not set")
        if not Path(cls.GOOGLE_CREDENTIALS_FILE).exists():
            errors.append(
                f"Google credentials file not found: {cls.GOOGLE_CREDENTIALS_FILE}. "
                "Download it from Google Cloud Console and run setup_google_auth.py"
            )
        return errors
