"""The avatar / profile dropdown in the top-right corner.

Locators and actions only - assertions live in
``validations/logout_validations.py``, expectations in
``config/profile_menu.py``.

Deliberately separate from ``LoginPage`` and from ``AppShell``: signing out is
its own concern, reachable from any authenticated page, so it must not be
coupled to how the session started or to what was tested in between.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from playwright.sync_api import Locator, Page

from config.profile_menu import ProfileMenuItem
from config.settings import settings
from pages.base_page import BasePage
from utils.logger import get_logger

if TYPE_CHECKING:  # avoids a circular import at runtime
    from pages.login_page import LoginPage

log = get_logger(__name__)


class ProfileMenu(BasePage):
    """The dropdown behind the top-right avatar."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # --- the avatar itself, always in the top bar once authenticated ---
        self.avatar: Locator = page.get_by_test_id("button-profile-menu")

        # --- the dropdown ---
        self.menu: Locator = page.get_by_role("menu")
        #: the account name line, e.g. "Forhad individual"
        self.account_name: Locator = self.menu.locator("p").first
        #: the account email line - located by *shape* (it is the entry holding
        #: an @), never by the expected value, so a wrong email still resolves
        #: and the assertion can report expected vs actual.
        self.account_email: Locator = self.menu.locator("p").filter(
            has_text=re.compile(r"@")
        )

    # --- actions ----------------------------------------------------
    def open(self) -> "ProfileMenu":
        """Click the avatar and wait for the dropdown to render."""
        log.info("opening the profile menu")
        self.avatar.wait_for(state="visible", timeout=settings.navigation_timeout)
        self.avatar.click()
        self.menu.first.wait_for(state="visible", timeout=settings.default_timeout)
        return self

    def close(self) -> "ProfileMenu":
        """Dismiss the dropdown without choosing anything."""
        self.page.keyboard.press("Escape")
        self.menu.first.wait_for(state="hidden", timeout=settings.default_timeout)
        return self

    def item(self, entry: ProfileMenuItem) -> Locator:
        """Locate one dropdown entry by its stable test id."""
        return self.page.get_by_test_id(entry.test_id)

    def logout(self, entry: ProfileMenuItem) -> "LoginPage":
        """Sign out and hand back the login page object.

        Returns the next page object, the way every navigation action in this
        project does, so a caller reads as a journey.
        """
        log.info("signing out")
        self.item(entry).click()

        from pages.login_page import LoginPage

        login_page = LoginPage(self.page)
        login_page.wait_until_settled()
        login_page.login_button.wait_for(
            state="visible", timeout=settings.navigation_timeout
        )
        return login_page

    # --- state ------------------------------------------------------
    @property
    def is_open(self) -> bool:
        return self.menu.first.is_visible()

    def displayed_email(self) -> str:
        """The email the dropdown shows for the current session."""
        if self.account_email.count() == 0:
            return ""
        return (self.account_email.first.inner_text() or "").strip()
