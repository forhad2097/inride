"""BasePage - navigation and waiting only. No assertions live here;
page-level assertions belong in ``validations/`` (see config/menus.py)."""

from __future__ import annotations

from playwright.sync_api import Page

from config.settings import REPORTS_DIR, settings
from utils.logger import get_logger

log = get_logger(__name__)


class BasePage:
    #: relative path of the page, overridden by each subclass
    PATH: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

    # --- navigation -------------------------------------------------
    def navigate(self, path: str | None = None) -> None:
        target = f"{settings.url}{path if path is not None else self.PATH}"
        log.info("navigating to %s", target)
        self.page.goto(target, wait_until="domcontentloaded",
                       timeout=settings.navigation_timeout)

    def wait_until_settled(self, timeout: int | None = None) -> None:
        """Wait for the SPA to stop fetching. Falls through on timeout rather
        than failing - the assertion that follows reports the real problem."""
        try:
            self.page.wait_for_load_state(
                "networkidle", timeout=timeout or settings.navigation_timeout
            )
        except Exception as exc:  # noqa: BLE001
            log.debug("networkidle not reached: %s", exc)

    @property
    def current_url(self) -> str:
        return self.page.url

    @property
    def path(self) -> str:
        return self.page.url.replace(settings.url, "", 1) or "/"

    # --- diagnostics ------------------------------------------------
    def screenshot(self, name: str) -> str:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return str(path)
