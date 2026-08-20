"""The post-login two-factor dialog chain - locators and actions only.

No assertions here; they live in ``validations/two_factor_validations.py``.

Screens 2 (Settings) and 3 (Setup) are the *same* dialog element re-rendered,
so every locator in those screens is scoped to that container and the screens
are told apart by their heading.

Nothing in this module enables two-factor authentication. ``Enable 2FA`` only
opens the setup screen; 2FA is switched on by ``Verify & Enable``, which this
suite never clicks.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config import two_factor as copy
from config.settings import settings
from pages.base_page import BasePage
from utils.logger import get_logger

log = get_logger(__name__)


class TwoFactorReminderDialog(BasePage):
    """Screen 1 - the reminder shown automatically after a successful login."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.container: Locator = page.get_by_test_id("dialog-two-factor-reminder")
        self.title: Locator = page.get_by_test_id("text-two-factor-reminder-title")
        self.description: Locator = page.get_by_test_id(
            "text-two-factor-reminder-description"
        )
        self.later_button: Locator = page.get_by_test_id(
            "button-two-factor-reminder-later"
        )
        self.open_settings_button: Locator = page.get_by_test_id(
            "button-two-factor-reminder-open-settings"
        )

    def wait_until_shown(self) -> "TwoFactorReminderDialog":
        self.container.wait_for(state="visible", timeout=settings.navigation_timeout)
        return self

    @property
    def is_open(self) -> bool:
        return self.container.is_visible()

    def open_security_settings(self) -> "TwoFactorSettingsDialog":
        log.info("opening the two-factor security settings")
        self.open_settings_button.click()
        return TwoFactorSettingsDialog(self.page).wait_until_shown()

    def dismiss(self) -> None:
        """'Maybe Later'. Read-only - changes no account setting."""
        self.later_button.click()
        self.container.wait_for(state="hidden", timeout=10000)


class TwoFactorSettingsDialog(BasePage):
    """Screens 2 and 3 - one dialog container, two rendered states."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.container: Locator = page.get_by_test_id("dialog-2fa-settings")

        # --- screen 2: settings ---
        self.title: Locator = self.container.get_by_role(
            "heading", name=copy.SETTINGS_TITLE, exact=True
        )
        self.subtitle: Locator = self.container.get_by_text(
            copy.SETTINGS_SUBTITLE, exact=True
        )
        self.status: Locator = self.container.get_by_text(
            copy.SETTINGS_STATUS_DISABLED, exact=True
        )
        self.description: Locator = self.container.get_by_text(
            copy.SETTINGS_DESCRIPTION, exact=True
        )
        self.enable_button: Locator = self.container.get_by_test_id("button-enable-2fa")
        # The X in the top-right corner. It carries no test id; its accessible
        # name comes from a screen-reader-only "Close" span.
        self.close_button: Locator = self.container.get_by_role(
            "button", name=copy.SETTINGS_CLOSE_BUTTON
        )

        # --- screen 3: setup ---
        self.setup_title: Locator = self.container.get_by_role(
            "heading", name=copy.SETUP_TITLE, exact=True
        )
        self.qr_instruction: Locator = self.container.get_by_text(
            copy.SETUP_QR_INSTRUCTION, exact=True
        )
        self.qr_code: Locator = self.container.get_by_test_id("img-qr-code")
        self.manual_code_label: Locator = self.container.get_by_text(
            copy.SETUP_MANUAL_CODE_LABEL, exact=True
        )
        #: dynamic per user and session - presence is asserted, value never is
        self.manual_code: Locator = self.container.get_by_test_id("text-secret")
        self.token_label: Locator = self.container.get_by_text(
            copy.SETUP_TOKEN_LABEL, exact=True
        )
        self.token_input: Locator = self.container.get_by_test_id("input-verify-token")
        self.cancel_button: Locator = self.container.get_by_test_id("button-cancel-setup")
        self.verify_button: Locator = self.container.get_by_test_id("button-verify-2fa")

    # --- state ------------------------------------------------------
    def wait_until_shown(self) -> "TwoFactorSettingsDialog":
        self.title.wait_for(state="visible", timeout=settings.navigation_timeout)
        return self

    def wait_until_setup_shown(self) -> "TwoFactorSettingsDialog":
        self.setup_title.wait_for(state="visible", timeout=settings.navigation_timeout)
        return self

    @property
    def is_open(self) -> bool:
        return self.container.is_visible()

    @property
    def is_showing_setup(self) -> bool:
        return self.setup_title.is_visible()

    # --- actions ----------------------------------------------------
    def enable_two_factor(self) -> "TwoFactorSettingsDialog":
        """Open the setup screen.

        This does *not* switch 2FA on - it only requests a setup secret. 2FA is
        activated by 'Verify & Enable', which this suite never clicks.
        """
        log.info("opening the two-factor setup screen")
        self.enable_button.click()
        return self.wait_until_setup_shown()

    def cancel_setup(self) -> "TwoFactorSettingsDialog":
        """Leave the setup screen; the settings screen is rendered again."""
        log.info("cancelling the two-factor setup")
        self.cancel_button.click()
        self.setup_title.wait_for(state="hidden", timeout=10000)
        return self.wait_until_shown()

    def close(self) -> None:
        log.info("closing the two-factor settings dialog")
        self.close_button.click()
        self.container.wait_for(state="hidden", timeout=10000)

    # --- read-only inspection of dynamic values ---------------------
    def manual_code_length(self) -> int:
        """Length only - the secret itself is never returned or logged."""
        return len(self.manual_code.inner_text().strip())

    def qr_code_is_rendered(self) -> bool:
        """True when the browser has actually decoded the image, not merely
        when the <img> element exists."""
        return bool(
            self.qr_code.evaluate(
                "img => img.complete && img.naturalWidth > 0 && img.naturalHeight > 0"
            )
        )
