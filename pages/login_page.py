"""Login page - locators and actions.

Assertions for this page live in ``validations/login_validations.py``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator, Page

from config.roles import Credentials
from pages.base_page import BasePage
from utils.logger import get_logger

if TYPE_CHECKING:  # avoids a circular import at runtime
    from pages.app_shell import AppShell

log = get_logger(__name__)


class LoginPage(BasePage):
    PATH = "/login"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # --- branding ---
        self.logo: Locator = page.get_by_alt_text("Trade Agent AI Logo")
        self.tagline: Locator = page.get_by_text(
            "AI-powered customer engagement management for automotive dealers"
        )

        # --- form ---
        self.email_input: Locator = page.get_by_test_id("input-login-email")
        self.email_label: Locator = page.get_by_text("Email", exact=True)
        self.password_input: Locator = page.get_by_test_id("input-login-password")
        self.password_label: Locator = page.get_by_text("Password", exact=True)
        self.show_password_button: Locator = page.get_by_role("button", name="Show password")
        self.forgot_password_link: Locator = page.get_by_test_id("link-forgot-password")
        self.login_button: Locator = page.get_by_test_id("button-login")
        self.sso_login_button: Locator = page.get_by_test_id("button-signin-sso")
        self.google_login_button: Locator = page.get_by_test_id("button-google-signin")

        # --- footer ---
        self.footer: Locator = page.get_by_role("contentinfo")
        self.footer_links: Locator = self.footer.get_by_role("link")

    # --- actions ----------------------------------------------------
    def open(self) -> "LoginPage":
        self.navigate("/")
        self.wait_until_settled()
        return self

    def login(self, credentials: Credentials) -> "AppShell":
        """Submit valid credentials and hand back the authenticated shell.

        The password is never logged; only the role and username are.
        """
        log.info("logging in as %s (%s)", credentials.role.value, credentials.username)
        self.email_input.fill(credentials.username)
        self.password_input.fill(credentials.password)
        self.login_button.click()

        from pages.app_shell import AppShell

        shell = AppShell(self.page)
        shell.wait_until_ready()
        return shell

    def submit_expecting_failure(self, username: str, password: str) -> "LoginPage":
        """Reserved for the negative-login cases of a later phase."""
        self.email_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        return self

    # --- dynamic discovery ------------------------------------------
    def visible_footer_items(self) -> list[dict[str, str]]:
        """Detect every footer link the page actually renders.

        Returns the accessible name (or aria-label for icon-only links), the
        href and the data-testid, so the footer can be asserted item by item
        without assuming a fixed order.
        """
        self.footer.first.wait_for(state="visible")
        return self.footer.first.evaluate(
            """(footer) => Array.from(footer.querySelectorAll('a')).filter(a => {
                const r = a.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            }).map(a => ({
                name: (a.innerText || '').trim() || (a.getAttribute('aria-label') || '').trim(),
                href: a.getAttribute('href') || '',
                testId: a.getAttribute('data-testid') || '',
            }))"""
        )

    def footer_link(self, test_id: str) -> Locator:
        return self.footer.get_by_test_id(test_id)
