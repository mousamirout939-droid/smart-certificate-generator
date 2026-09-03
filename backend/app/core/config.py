"""
Application configuration.

All secrets and environment-specific values are loaded from environment
variables (via a .env file in development). Nothing sensitive is hardcoded.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present (development convenience)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_bool(key: str, default: bool) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_certificate.db")

    # --- Auth / JWT ---
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    # --- SMTP / Email ---
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587") or "587")
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "")

    @property
    def SMTP_CONFIGURED(self) -> bool:
        return bool(self.SMTP_HOST and self.SMTP_USERNAME and self.SMTP_PASSWORD and self.SMTP_FROM)

    # --- Organization / Certificate branding ---
    ORGANIZATION_NAME: str = os.getenv("ORGANIZATION_NAME", "Acme Learning & Development")
    CERTIFICATE_SIGNATURE_NAME: str = os.getenv("CERTIFICATE_SIGNATURE_NAME", "Director, Learning & Development")

    # --- Automation / Scheduler ---
    AUTOMATION_INTERVAL_MINUTES: int = int(os.getenv("AUTOMATION_INTERVAL_MINUTES", "30"))
    ENABLE_AUTOMATION: bool = _get_bool("ENABLE_AUTOMATION", True)

    # --- Misc ---
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    DEFAULT_TARGET_HOURS: float = float(os.getenv("DEFAULT_TARGET_HOURS", "50"))

    # --- Paths ---
    CERTIFICATES_DIR: Path = BASE_DIR / "generated" / "certificates"


settings = Settings()
settings.CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
