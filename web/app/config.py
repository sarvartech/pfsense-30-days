"""Platforma sozlamalari — barchasi environment o'zgaruvchilardan o'qiladi."""
from __future__ import annotations

import os
import warnings
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(self) -> None:
        self.site_name = os.getenv("SITE_NAME", "Men Tarmoq")
        self.site_tagline = os.getenv(
            "SITE_TAGLINE", "Tarmoq texnologiyalarini nazariya + jonli laboratoriya orqali o'rganing"
        )
        self.secret_key = os.getenv("SECRET_KEY", "dev-insecure-change-me")
        default_db = REPO_ROOT / "web" / "data" / "platform.db"
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{default_db}")
        self.content_dir = Path(os.getenv("CONTENT_DIR", str(REPO_ROOT))).resolve()

        # Lab agent (home serverda, WireGuard orqali: http://10.99.0.2:8090)
        self.lab_agent_url = os.getenv("LAB_AGENT_URL", "").rstrip("/")
        self.lab_agent_token = os.getenv("LAB_AGENT_TOKEN", "")
        self.lab_ttl_minutes = int(os.getenv("LAB_TTL_MINUTES", "90"))
        self.max_labs_per_user = int(os.getenv("MAX_LABS_PER_USER", "1"))
        self.term_base_path = os.getenv("TERM_BASE_PATH", "/term").rstrip("/")

        self.admin_emails = {
            e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()
        }
        self.https_only = _bool(os.getenv("HTTPS_ONLY"), False)
        self.allow_registration = _bool(os.getenv("ALLOW_REGISTRATION"), True)
        self.debug = _bool(os.getenv("DEBUG"), False)

        if self.secret_key == "dev-insecure-change-me" and self.https_only:
            warnings.warn("SECRET_KEY production rejimida o'rnatilmagan!", stacklevel=1)

    @property
    def labs_enabled(self) -> bool:
        return bool(self.lab_agent_url and self.lab_agent_token)


settings = Settings()
