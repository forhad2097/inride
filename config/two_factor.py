"""Expected content of the post-login two-factor dialog chain.

Data only - no locators and no logic. ``pages/two_factor.py`` knows *how* to
find these things; this module records *what* must be there, so a wording change
in the application is a one-line edit here.

The chain is three screens:

1. **Reminder**  ``dialog-two-factor-reminder`` - shown automatically after login
2. **Settings**  ``dialog-2fa-settings`` - reached via "Open Security Settings"
3. **Setup**     the *same* dialog element, re-rendered after "Enable 2FA"

Screens 2 and 3 share one dialog container, so they are told apart by their
heading, never by the container's identity.
"""

from __future__ import annotations

# ------------------------------------------------ 1. reminder dialog
REMINDER_TITLE = "Protect your account with 2FA"
REMINDER_DESCRIPTION = (
    "Two-factor authentication is currently turned off for your account. "
    "Please enable it from Profile > Security Settings to add an extra "
    "verification step when you sign in."
)
REMINDER_LATER_BUTTON = "Maybe Later"
REMINDER_OPEN_SETTINGS_BUTTON = "Open Security Settings"

# ------------------------------------------------ 2. settings dialog
SETTINGS_TITLE = "Two-Factor Authentication"
SETTINGS_SUBTITLE = "Add an extra layer of security to your account"
SETTINGS_STATUS_DISABLED = "2FA is Disabled"
SETTINGS_DESCRIPTION = (
    "Enable 2FA to secure your account with time-based one-time passwords"
)
SETTINGS_ENABLE_BUTTON = "Enable 2FA"
SETTINGS_CLOSE_BUTTON = "Close"

# --------------------------------------------------- 3. setup dialog
SETUP_TITLE = "Setup Two-Factor Authentication"
SETUP_QR_INSTRUCTION = "Scan this QR code with your authenticator app"
SETUP_QR_ALT = "QR Code"
SETUP_MANUAL_CODE_LABEL = "Or enter this code manually:"
SETUP_TOKEN_LABEL = "Enter the 6-digit code from your app"
SETUP_TOKEN_PLACEHOLDER = "000000"
SETUP_TOKEN_MAX_LENGTH = "6"
SETUP_CANCEL_BUTTON = "Cancel"
SETUP_VERIFY_BUTTON = "Verify & Enable"

#: Values that are regenerated per user and per session. Their *presence* is
#: asserted; their content never is.
DYNAMIC_VALUES = ("QR code image", "manual setup code")
