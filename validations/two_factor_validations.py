"""Assertions for the post-login two-factor dialog chain.

Expected values come from ``config/two_factor.py``; locators come from
``pages/two_factor.py``. Nothing in this module knows a selector.

Dynamic values - the QR image and the manual setup code - are asserted for
presence only. Their content is regenerated per user and per session, so
asserting it would be asserting noise. The manual code is additionally treated
as a secret: it never appears in an assertion description or an expected/actual
value.
"""

from __future__ import annotations

from config import two_factor as copy
from config.roles import Role
from pages.two_factor import TwoFactorReminderDialog, TwoFactorSettingsDialog
from utils.verification import Verifier


class TwoFactorValidations:
    """Every assertion is named so the report reads as a checklist."""

    def __init__(self, verify: Verifier, role: Role) -> None:
        self.verify = verify
        self.prefix = f"{role.display_name} - 2FA"

    # ============================================ 1. reminder dialog
    def validate_reminder_dialog(self, dialog: TwoFactorReminderDialog) -> None:
        """The popup the application raises by itself after a successful login."""
        self.verify.visible(
            dialog.container, f"{self.prefix} Reminder popup is displayed after login"
        )
        self.verify.visible(
            dialog.title, f"{self.prefix} Reminder title '{copy.REMINDER_TITLE}' is visible"
        )
        self.verify.has_text(
            dialog.title,
            copy.REMINDER_TITLE,
            f"{self.prefix} Reminder title text is exactly '{copy.REMINDER_TITLE}'",
        )
        self.verify.visible(
            dialog.description, f"{self.prefix} Reminder description is visible"
        )
        self.verify.has_text(
            dialog.description,
            copy.REMINDER_DESCRIPTION,
            f"{self.prefix} Reminder description text is complete and correct",
        )
        self.verify.visible(
            dialog.later_button,
            f"{self.prefix} Reminder '{copy.REMINDER_LATER_BUTTON}' button is visible",
        )
        self.verify.has_text(
            dialog.later_button,
            copy.REMINDER_LATER_BUTTON,
            f"{self.prefix} Reminder button text is '{copy.REMINDER_LATER_BUTTON}'",
        )
        self.verify.visible(
            dialog.open_settings_button,
            f"{self.prefix} Reminder '{copy.REMINDER_OPEN_SETTINGS_BUTTON}' button is visible",
        )
        self.verify.has_text(
            dialog.open_settings_button,
            copy.REMINDER_OPEN_SETTINGS_BUTTON,
            f"{self.prefix} Reminder button text is '{copy.REMINDER_OPEN_SETTINGS_BUTTON}'",
        )

    # ============================================ 2. settings dialog
    def validate_settings_dialog(self, dialog: TwoFactorSettingsDialog) -> None:
        self.verify.visible(
            dialog.container, f"{self.prefix} Settings popup is displayed"
        )
        self.verify.visible(
            dialog.title, f"{self.prefix} Settings title '{copy.SETTINGS_TITLE}' is visible"
        )
        self.verify.has_text(
            dialog.title,
            copy.SETTINGS_TITLE,
            f"{self.prefix} Settings title text is exactly '{copy.SETTINGS_TITLE}'",
        )
        self.verify.visible(
            dialog.subtitle, f"{self.prefix} Settings subtitle is visible"
        )
        self.verify.has_text(
            dialog.subtitle,
            copy.SETTINGS_SUBTITLE,
            f"{self.prefix} Settings subtitle text is '{copy.SETTINGS_SUBTITLE}'",
        )
        self.verify.visible(
            dialog.status,
            f"{self.prefix} Status '{copy.SETTINGS_STATUS_DISABLED}' is visible",
        )
        self.verify.has_text(
            dialog.status,
            copy.SETTINGS_STATUS_DISABLED,
            f"{self.prefix} Status text is exactly '{copy.SETTINGS_STATUS_DISABLED}'",
        )
        self.verify.visible(
            dialog.description, f"{self.prefix} Settings description is visible"
        )
        self.verify.has_text(
            dialog.description,
            copy.SETTINGS_DESCRIPTION,
            f"{self.prefix} Settings description text is complete and correct",
        )
        self.verify.visible(
            dialog.enable_button,
            f"{self.prefix} '{copy.SETTINGS_ENABLE_BUTTON}' button is visible",
        )
        self.verify.has_text(
            dialog.enable_button,
            copy.SETTINGS_ENABLE_BUTTON,
            f"{self.prefix} Enable button text is '{copy.SETTINGS_ENABLE_BUTTON}'",
        )

    def validate_close_control(self, dialog: TwoFactorSettingsDialog) -> None:
        """The X in the top-right corner of the settings popup."""
        self.verify.has_count(
            dialog.close_button, 1, f"{self.prefix} Settings popup has a Close (X) control"
        )
        self.verify.visible(
            dialog.close_button, f"{self.prefix} Settings popup Close (X) control is visible"
        )
        self.verify.custom(
            f"{self.prefix} Settings popup Close (X) control is enabled",
            lambda: _assert(
                dialog.close_button.first.is_enabled(), "the Close control is disabled"
            ),
            expected="enabled",
            actual="enabled" if dialog.close_button.first.is_enabled() else "disabled",
        )

    # =============================================== 3. setup dialog
    def validate_setup_dialog(self, dialog: TwoFactorSettingsDialog) -> None:
        self.verify.visible(
            dialog.setup_title, f"{self.prefix} Setup title '{copy.SETUP_TITLE}' is visible"
        )
        self.verify.has_text(
            dialog.setup_title,
            copy.SETUP_TITLE,
            f"{self.prefix} Setup title text is exactly '{copy.SETUP_TITLE}'",
        )
        self.verify.visible(
            dialog.qr_instruction, f"{self.prefix} QR code instruction is visible"
        )
        self.verify.has_text(
            dialog.qr_instruction,
            copy.SETUP_QR_INSTRUCTION,
            f"{self.prefix} QR code instruction text is '{copy.SETUP_QR_INSTRUCTION}'",
        )

    def validate_qr_code(self, dialog: TwoFactorSettingsDialog) -> None:
        """Presence only. The QR encodes a per-session secret, so its value,
        content and pixels are deliberately not asserted."""
        self.verify.visible(dialog.qr_code, f"{self.prefix} QR code image is visible")
        self.verify.has_attribute(
            dialog.qr_code,
            "alt",
            copy.SETUP_QR_ALT,
            f"{self.prefix} QR code image has the accessible name '{copy.SETUP_QR_ALT}'",
        )
        self.verify.custom(
            f"{self.prefix} QR code image is actually rendered by the browser",
            lambda: _assert(
                dialog.qr_code_is_rendered(), "the QR image element exists but has no pixels"
            ),
            expected="image decoded with a non-zero size",
            actual="rendered" if dialog.qr_code_is_rendered() else "not rendered",
        )

    def validate_manual_code(self, dialog: TwoFactorSettingsDialog) -> None:
        """Presence only - the setup secret is never read into the report."""
        self.verify.visible(
            dialog.manual_code_label,
            f"{self.prefix} '{copy.SETUP_MANUAL_CODE_LABEL}' text is visible",
        )
        self.verify.has_text(
            dialog.manual_code_label,
            copy.SETUP_MANUAL_CODE_LABEL,
            f"{self.prefix} Manual code label text is '{copy.SETUP_MANUAL_CODE_LABEL}'",
        )
        self.verify.visible(
            dialog.manual_code, f"{self.prefix} Manual setup code element is visible"
        )
        length = dialog.manual_code_length()
        self.verify.custom(
            f"{self.prefix} Manual setup code is populated (value not recorded - it is a secret)",
            lambda: _assert(length > 0, "the manual setup code is empty"),
            expected="a non-empty value",
            actual=f"{length} characters",
        )

    def validate_token_input(self, dialog: TwoFactorSettingsDialog) -> None:
        """The 6-digit field is validated, never filled - no code is submitted."""
        self.verify.visible(
            dialog.token_label,
            f"{self.prefix} '{copy.SETUP_TOKEN_LABEL}' text is visible",
        )
        self.verify.has_text(
            dialog.token_label,
            copy.SETUP_TOKEN_LABEL,
            f"{self.prefix} 6-digit code label text is '{copy.SETUP_TOKEN_LABEL}'",
        )
        self.verify.has_count(
            dialog.token_input, 1, f"{self.prefix} 6-digit code input field exists"
        )
        self.verify.visible(
            dialog.token_input, f"{self.prefix} 6-digit code input field is visible"
        )
        enabled = dialog.token_input.first.is_enabled()
        self.verify.custom(
            f"{self.prefix} 6-digit code input field is enabled and ready for entry",
            lambda: _assert(enabled, "the 6-digit code input is disabled"),
            expected="enabled",
            actual="enabled" if enabled else "disabled",
        )
        self.verify.has_attribute(
            dialog.token_input,
            "placeholder",
            copy.SETUP_TOKEN_PLACEHOLDER,
            f"{self.prefix} 6-digit code input placeholder is '{copy.SETUP_TOKEN_PLACEHOLDER}'",
        )
        self.verify.has_attribute(
            dialog.token_input,
            "maxlength",
            copy.SETUP_TOKEN_MAX_LENGTH,
            f"{self.prefix} 6-digit code input accepts at most "
            f"{copy.SETUP_TOKEN_MAX_LENGTH} characters",
        )

    def validate_setup_buttons(self, dialog: TwoFactorSettingsDialog) -> None:
        """Both buttons are asserted. 'Verify & Enable' is never clicked - doing
        so would switch two-factor authentication on for a shared QA account."""
        self.verify.visible(
            dialog.cancel_button,
            f"{self.prefix} Setup '{copy.SETUP_CANCEL_BUTTON}' button is visible",
        )
        self.verify.has_text(
            dialog.cancel_button,
            copy.SETUP_CANCEL_BUTTON,
            f"{self.prefix} Setup Cancel button text is '{copy.SETUP_CANCEL_BUTTON}'",
        )
        self.verify.visible(
            dialog.verify_button,
            f"{self.prefix} Setup '{copy.SETUP_VERIFY_BUTTON}' button is visible",
        )
        self.verify.has_text(
            dialog.verify_button,
            copy.SETUP_VERIFY_BUTTON,
            f"{self.prefix} Setup submit button text is '{copy.SETUP_VERIFY_BUTTON}' "
            f"(the UI has no separate 'Verify' button)",
        )

    # ============================================== 4. state changes
    def validate_setup_closed_and_settings_restored(
        self, dialog: TwoFactorSettingsDialog
    ) -> None:
        """After Cancel: the setup screen is gone and the settings screen is back."""
        self.verify.custom(
            f"{self.prefix} Setup popup is closed after Cancel",
            lambda: _assert(
                not dialog.is_showing_setup, "the setup screen is still displayed"
            ),
            expected="setup screen hidden",
            actual="hidden" if not dialog.is_showing_setup else "still visible",
        )
        self.verify.visible(
            dialog.title, f"{self.prefix} Settings popup is displayed again after Cancel"
        )
        self.verify.has_text(
            dialog.status,
            copy.SETTINGS_STATUS_DISABLED,
            f"{self.prefix} Status is still '{copy.SETTINGS_STATUS_DISABLED}' - "
            f"cancelling setup left the account unchanged",
        )

    def validate_settings_closed(self, dialog: TwoFactorSettingsDialog) -> None:
        self.verify.custom(
            f"{self.prefix} Settings popup is closed after clicking Close (X)",
            lambda: _assert(not dialog.is_open, "the settings popup is still displayed"),
            expected="settings popup hidden",
            actual="hidden" if not dialog.is_open else "still visible",
        )

    def validate_reminder_closed(self, dialog: TwoFactorReminderDialog) -> None:
        self.verify.custom(
            f"{self.prefix} Reminder popup is no longer displayed",
            lambda: _assert(not dialog.is_open, "the reminder popup is still displayed"),
            expected="reminder popup hidden",
            actual="hidden" if not dialog.is_open else "still visible",
        )


def _assert(condition: bool, message: str) -> None:
    assert condition, message
