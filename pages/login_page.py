"""Login page - locators and actions.

Locators are grouped by the region of the page they belong to: login form,
password visibility, footer branding, legal, contact info, social and
copyright. Assertions for all of them live in
``validations/login_validations.py``; expected values live in
``config/login_page.py``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator, Page

from config import login_page as copy
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
        self.logo: Locator = page.get_by_alt_text(copy.LOGO_ALT)
        self.tagline: Locator = page.get_by_text(copy.TAGLINE)

        # --- login form ---
        # "Log In" is rendered twice: the card title and the submit button.
        # ``and_`` keeps the title unambiguous without relying on DOM order.
        self.login_title: Locator = page.get_by_text(
            copy.LOGIN_TITLE, exact=True
        ).and_(page.locator("div"))
        self.email_label: Locator = page.get_by_text(copy.EMAIL_LABEL, exact=True)
        self.email_input: Locator = page.get_by_test_id("input-login-email")
        self.password_label: Locator = page.get_by_text(copy.PASSWORD_LABEL, exact=True)
        self.password_input: Locator = page.get_by_test_id("input-login-password")
        self.login_button: Locator = page.get_by_test_id("button-login")
        self.forgot_password_link: Locator = page.get_by_test_id("link-forgot-password")
        self.sso_login_button: Locator = page.get_by_test_id("button-signin-sso")
        self.google_login_button: Locator = page.get_by_test_id("button-google-signin")

        # --- password visibility ---
        # One button whose accessible name flips between the two states.
        self.show_password_button: Locator = page.get_by_role(
            "button", name=copy.SHOW_PASSWORD_LABEL
        )
        self.hide_password_button: Locator = page.get_by_role(
            "button", name=copy.HIDE_PASSWORD_LABEL
        )

        # --- footer: container + branding ---
        self.footer: Locator = page.get_by_role("contentinfo")
        self.footer_links: Locator = self.footer.get_by_role("link")
        # exact=True, otherwise the header logo ("Trade Agent AI Logo") also matches
        self.footer_logo: Locator = page.get_by_role(
            "img", name=copy.FOOTER_LOGO_ALT, exact=True
        )

        # --- footer: legal ---
        self.legal_section: Locator = self.footer.get_by_text(
            copy.LEGAL_SECTION, exact=True
        )
        self.ai_terms_link: Locator = page.get_by_test_id("link-ai-terms")
        self.privacy_policy_link: Locator = page.get_by_test_id("link-privacy")
        self.cookies_policy_link: Locator = page.get_by_test_id("link-cookies")

        # --- footer: contact info ---
        self.contact_info_section: Locator = self.footer.get_by_text(
            copy.CONTACT_SECTION, exact=True
        )
        self.address: Locator = page.get_by_test_id("text-address")
        self.phone_link: Locator = page.get_by_test_id("link-phone")
        self.email_link: Locator = page.get_by_test_id("link-email")

        # --- footer: social + copyright ---
        self.facebook_link: Locator = page.get_by_test_id("link-facebook")
        self.instagram_link: Locator = page.get_by_test_id("link-instagram")
        self.linkedin_link: Locator = page.get_by_test_id("link-linkedin")
        self.twitter_link: Locator = page.get_by_test_id("link-twitter")
        self.copyright_text: Locator = page.get_by_test_id("text-copyright")

    # --- navigation -------------------------------------------------
    def open(self) -> "LoginPage":
        self.navigate("/")
        self.wait_until_settled()
        return self

    def footer_link(self, test_id: str) -> Locator:
        """Any footer link by its stable test id (used for the data-driven sweep)."""
        return self.footer.get_by_test_id(test_id)

    # --- form actions -----------------------------------------------
    def fill_credentials(self, credentials: Credentials) -> "LoginPage":
        """Type the credentials without submitting, so the password-visibility
        behaviour can be exercised against a real value.

        The password is never logged; only the role and username are.
        """
        log.info(
            "entering credentials for %s (%s)",
            credentials.role.value,
            credentials.username,
        )
        self.email_input.fill(credentials.username)
        self.password_input.fill(credentials.password)
        return self

    def submit(self, *, dismiss_reminder: bool = True) -> "AppShell":
        """Submit the form and hand back the authenticated shell.

        ``dismiss_reminder=False`` leaves the post-login two-factor reminder
        popup on screen. The navigation suites want it gone (it overlays every
        click); the two-factor suite wants it intact so it can be asserted.
        """
        self.login_button.click()

        from pages.app_shell import AppShell

        shell = AppShell(self.page)
        shell.wait_until_ready(dismiss_reminder=dismiss_reminder)
        return shell

    def login(self, credentials: Credentials, *, dismiss_reminder: bool = True) -> "AppShell":
        """Fill the form and submit it in one step."""
        return self.fill_credentials(credentials).submit(dismiss_reminder=dismiss_reminder)

    def submit_expecting_failure(self, username: str, password: str) -> "LoginPage":
        """Reserved for the negative-login cases of a later phase."""
        self.email_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        return self

    # --- password visibility actions --------------------------------
    def password_field_type(self) -> str:
        """``'password'`` while masked, ``'text'`` once revealed."""
        return self.password_input.get_attribute("type") or ""

    def password_is_masked(self) -> bool:
        return self.password_field_type() == copy.MASKED_TYPE

    def entered_password_matches(self, expected: str) -> bool:
        """Compare the field's value without ever returning or logging it."""
        return self.password_input.input_value() == expected

    def show_password(self) -> "LoginPage":
        log.info("revealing the password")
        self.show_password_button.click()
        return self

    def hide_password(self) -> "LoginPage":
        log.info("masking the password again")
        self.hide_password_button.click()
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
