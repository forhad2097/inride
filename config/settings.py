"""Environment-driven configuration.

Nothing in the test suite reads ``os.environ`` directly except this module and
``config.roles`` - a new environment means a new ``.env``, not a code change.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / "reports"
SCREENSHOT_DIR = REPORTS_DIR / "screenshots"

load_dotenv(ROOT_DIR / ".env")


def _bool(name: str, default: str = "true") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes"}


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    # --- target application ---
    base_url: str = os.getenv("BASE_URL", "https://agentai-qa.inride.com")

    # --- browser ---
    headless: bool = _bool("HEADLESS")
    slow_mo: int = _int("SLOW_MO", 0)
    default_timeout: int = _int("DEFAULT_TIMEOUT", 20000)
    navigation_timeout: int = _int("NAVIGATION_TIMEOUT", 60000)

    # --- visual highlighting (requirement 3 / 12) ---
    highlight_enabled: bool = _bool("HIGHLIGHT_ENABLED")
    #: how long the yellow highlight stays on screen before the assertion runs
    highlight_ms: int = _int("HIGHLIGHT_MS", 350)
    highlight_background: str = os.getenv("HIGHLIGHT_BACKGROUND", "#FFEB3B")
    highlight_outline: str = os.getenv("HIGHLIGHT_OUTLINE", "3px solid #FFC107")
    highlight_outline_color: str = os.getenv("HIGHLIGHT_OUTLINE_COLOR", "#F57F17")
    #: forced text colour, so a light-on-dark label stays readable on yellow
    highlight_foreground: str = os.getenv("HIGHLIGHT_FOREGROUND", "#1A1A1A")
    #: elements that fail keep a red marker so the failure screenshot shows them
    failure_outline: str = os.getenv("FAILURE_OUTLINE", "3px solid #E53935")
    failure_outline_color: str = os.getenv("FAILURE_OUTLINE_COLOR", "#C62828")

    @property
    def url(self) -> str:
        return self.base_url.rstrip("/")


settings = Settings()
