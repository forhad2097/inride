"""The authenticated application shell: sidebar navigation + top bar.

Every menu is reached through this object, so a change in the navigation
markup is a one-line change here rather than a change in fourteen tests.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.menus import MenuItem
from config.settings import settings
from pages.base_page import BasePage
from utils.logger import get_logger

log = get_logger(__name__)


class AppShell(BasePage):
    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.sidebar_toggle: Locator = page.get_by_test_id("button-sidebar-toggle")
        self.theme_toggle: Locator = page.get_by_test_id("button-theme-toggle")
        self.notifications_button: Locator = page.get_by_test_id("button-notifications")
        self.profile_menu: Locator = page.get_by_test_id("button-profile-menu")

        # Post-login reminder dialog. Dismissing it is read-only - it does not
        # change any account setting.
        self.two_factor_dialog: Locator = page.get_by_test_id("dialog-two-factor-reminder")
        self.two_factor_dismiss: Locator = page.get_by_test_id(
            "button-two-factor-reminder-later"
        )

        # Page-level primitives shared by every destination page.
        self.page_title: Locator = page.locator("main h1").first
        self.page_description: Locator = page.get_by_test_id("text-page-description")

    # --- readiness --------------------------------------------------
    def wait_until_ready(self) -> "AppShell":
        """Block until the authenticated shell is usable: the profile menu is
        rendered and the post-login reminder dialog is out of the way."""
        self.profile_menu.wait_for(state="visible", timeout=settings.navigation_timeout)
        self.dismiss_two_factor_reminder()
        return self

    def dismiss_two_factor_reminder(self) -> bool:
        """Close the '2FA is off' reminder if it is showing.

        The dialog renders a full-screen overlay that intercepts every click,
        so this must happen before any navigation. Returns whether it was shown.
        """
        try:
            self.two_factor_dismiss.wait_for(state="visible", timeout=8000)
        except Exception:  # noqa: BLE001 - dialog not shown is the happy case
            return False
        log.info("dismissing the two-factor reminder dialog")
        self.two_factor_dismiss.click()
        self.two_factor_dialog.wait_for(state="hidden", timeout=10000)
        return True

    @property
    def is_authenticated(self) -> bool:
        return self.profile_menu.is_visible()

    # --- navigation -------------------------------------------------
    def menu_link(self, item: MenuItem) -> Locator:
        """Locate a sidebar entry by its stable test id."""
        return self.page.get_by_test_id(item.test_id)

    def open_menu(self, item: MenuItem) -> "AppShell":
        """Click a sidebar entry and wait for its page to settle."""
        log.info("opening menu: %s", item.label)
        self.dismiss_two_factor_reminder()
        link = self.menu_link(item)
        link.scroll_into_view_if_needed(timeout=10000)
        # The staging SPA can be slow to hand over a route under load, so a
        # menu click gets the navigation budget, not the shorter element one.
        link.click(timeout=settings.navigation_timeout)
        self.wait_until_settled()
        return self

    def heading(self, text: str) -> Locator:
        """The primary page header, matched on its text so a DOM change in the
        surrounding layout does not break the locator."""
        return self.page.get_by_role("heading", name=text, exact=True)

    def text(self, value: str, *, exact: bool = False) -> Locator:
        return self.page.get_by_text(value, exact=exact)

    def logout(self) -> None:
        """Reserved for the multi-role phase."""
        self.profile_menu.click()
        self.page.get_by_role("menuitem", name="Log out").click()
