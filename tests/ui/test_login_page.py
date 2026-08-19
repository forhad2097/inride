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
from utils.logger import get_logger
from utils.verification import Verifier
from validations.login_validations import LoginPageValidations
from validations.navigation_validations import NavigationValidations

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
