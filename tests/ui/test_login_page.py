"""Login page validation, then the login itself.

Everything below runs in the **one shared guest window** (``guest_session``) -
the same Playwright browser, context and page from the first assertion to the
successful login. No test opens a second browser, context, page or driver.

| Case                                          | Priority | Covers                    |
|-----------------------------------------------|----------|---------------------------|
| branding and login form are displayed         | P0       | LOGIN-01 .. LOGIN-12      |
| footer is complete (logo, legal, contact,     | P1       | LOGIN-13 .. LOGIN-20      |
| social, copyright) and detected dynamically   |          |                           |
| password show/hide toggle, then valid login   | P0       | LOGIN-21 .. LOGIN-28      |

The login case runs last on purpose: it is the only one that changes the
window's authentication state, and it hands that state back afterwards.
"""

import pytest
from playwright.sync_api import Page

from config.roles import Credentials, Role
from pages.login_page import LoginPage
from pages.two_factor import TwoFactorReminderDialog
from utils.logger import get_logger
from utils.verification import Verifier
from validations.login_validations import LoginPageValidations
from validations.navigation_validations import NavigationValidations
from validations.two_factor_validations import TwoFactorValidations

log = get_logger(__name__)


@pytest.fixture
def login_validations(verify: Verifier, login_page: LoginPage, role: Role):
    login_page.open()
    return LoginPageValidations(verify, login_page, role)


@pytest.fixture
def signed_out_afterwards(guest_session: Page):
    """Hand the shared guest window back signed out.

    Same browser, same context, same page - only the stored authentication is
    cleared, so a re-run or any later test still starts from the login page.
    """
    yield
    try:
        guest_session.context.clear_cookies()
        guest_session.evaluate(
            "() => { window.localStorage.clear(); window.sessionStorage.clear(); }"
        )
        log.info("guest window returned to its signed-out state")
    except Exception as exc:  # noqa: BLE001 - cleanup must never fail a green test
        log.debug("could not reset the guest window: %s", exc)


# ------------------------------------------------------- UI validation
@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.login
def test_login_page_shows_branding_and_login_form(login_validations: LoginPageValidations):
    login_validations.validate_branding()
    login_validations.validate_login_form()


@pytest.mark.smoke
@pytest.mark.login
def test_login_page_footer_is_complete(login_validations: LoginPageValidations):
    """Footer logo, Legal, Contact Info, social icons and the copyright line."""
    login_validations.validate_footer()


# ------------------------------------------------- functional login
@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.login
def test_password_visibility_toggles_then_valid_user_logs_in(
    login_validations: LoginPageValidations,
    login_page: LoginPage,
    platform_admin: Credentials,
    verify: Verifier,
    role: Role,
    signed_out_afterwards,
):
    """Type the credentials, exercise show/hide, then sign in - one window."""
    password = platform_admin.password

    # --- 1. credentials entered, password hidden by default ---
    login_page.fill_credentials(platform_admin)
    login_validations.validate_password_is_masked(password, stage="after it is typed in")

    # --- 2. reveal it ---
    login_page.show_password()
    login_validations.validate_password_is_revealed(password)
    login_validations.validate_toggle_offers_hide()

    # --- 3. hide it again; the value must survive the round trip ---
    login_page.hide_password()
    login_validations.validate_password_is_masked(password, stage="after hiding it again")
    login_validations.validate_toggle_offers_show()

    # --- 4. sign in, in the same window ---
    shell = login_page.submit()

    navigation = NavigationValidations(verify, shell, role)
    navigation.validate_logged_in()
    verify.record_info(
        f"{role.display_name} - Landing page after a successful login", shell.current_url
    )


# --------------------------------------------- post-login 2FA flow
@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.login
@pytest.mark.two_factor
def test_post_login_two_factor_flow_can_be_reviewed_and_dismissed(
    login_page: LoginPage,
    platform_admin: Credentials,
    verify: Verifier,
    role: Role,
    signed_out_afterwards,
):
    """Log in, then walk the whole two-factor dialog chain and back out of it.

    Same browser, same context, same page as every other test in this file.

    Read-only by design. ``Enable 2FA`` only requests a setup secret and opens
    the setup screen; two-factor authentication is switched on by
    ``Verify & Enable``, which is asserted but **never clicked** - doing so
    would lock a shared QA account behind an authenticator app.
    """
    two_factor = TwoFactorValidations(verify, role)

    # --- 1. log in, leaving the reminder popup on screen to be asserted ---
    login_page.open()
    shell = login_page.login(platform_admin, dismiss_reminder=False)

    reminder = TwoFactorReminderDialog(shell.page).wait_until_shown()
    two_factor.validate_reminder_dialog(reminder)

    # --- 2. "Open Security Settings", not "Maybe Later" ---
    settings_dialog = reminder.open_security_settings()
    two_factor.validate_settings_dialog(settings_dialog)
    two_factor.validate_close_control(settings_dialog)

    # --- 3. "Enable 2FA" opens the setup screen ---
    settings_dialog.enable_two_factor()
    two_factor.validate_setup_dialog(settings_dialog)
    two_factor.validate_qr_code(settings_dialog)
    two_factor.validate_manual_code(settings_dialog)
    two_factor.validate_token_input(settings_dialog)
    two_factor.validate_setup_buttons(settings_dialog)

    # --- 4. Cancel returns to the settings screen ---
    settings_dialog.cancel_setup()
    two_factor.validate_setup_closed_and_settings_restored(settings_dialog)

    # --- 5. the X closes the settings popup ---
    settings_dialog.close()
    two_factor.validate_settings_closed(settings_dialog)
    two_factor.validate_reminder_closed(reminder)

    # --- 6. back in the authenticated application ---
    NavigationValidations(verify, shell, role).validate_logged_in()
    verify.record_info(
        f"{role.display_name} - Application state after closing the 2FA dialogs",
        shell.current_url,
    )
