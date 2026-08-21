"""Login page validation, then the login itself.

Everything below runs in the **one shared guest window** (``guest_session``) -
the same Playwright browser, context and page from the first assertion to the
successful login. No test opens a second browser, context, page or driver.

The journey itself lives in ``flows/login_flow.py``. This module splits it into
three separately-named cases so a failure says *which part* of the login broke;
``tests/ui/test_login_logout.py`` runs the same flow end to end and then signs
out again.

| Case                                          | Priority | Covers                    |
|-----------------------------------------------|----------|---------------------------|
| branding and login form are displayed         | P0       | LOGIN-01 .. LOGIN-12      |
| footer is complete (logo, legal, contact,     | P1       | LOGIN-13 .. LOGIN-20      |
| social, copyright) and detected dynamically   |          |                           |
| password show/hide, sign in, full 2FA dialog  | P0       | LOGIN-21 .. LOGIN-28,     |
| chain, back to the authenticated dashboard    |          | 2FA-01 .. 2FA-13          |

The login case runs last on purpose: it is the only one that changes the
window's authentication state, and it hands that state back afterwards.
"""

import pytest
from playwright.sync_api import Page

from config.roles import Credentials, Role
from flows.login_flow import LoginFlow
from pages.login_page import LoginPage
from utils.logger import get_logger
from utils.verification import Verifier

log = get_logger(__name__)


@pytest.fixture
def login_flow(
    verify: Verifier, login_page: LoginPage, role: Role, login_credentials: Credentials
) -> LoginFlow:
    """The login journey, pointed at whichever role the ``role`` fixture holds."""
    login_page.open()
    return LoginFlow(verify, login_page, role, login_credentials)


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
def test_login_page_shows_branding_and_login_form(login_flow: LoginFlow):
    login_flow.validate_login_page_ui()


@pytest.mark.smoke
@pytest.mark.login
def test_login_page_footer_is_complete(login_flow: LoginFlow):
    """Footer logo, Legal, Contact Info, social icons and the copyright line."""
    login_flow.validate_footer()


# ---------------------------- functional login through the full 2FA flow
@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.login
@pytest.mark.two_factor
def test_login_flow_completes_through_two_factor_and_reaches_the_dashboard(
    login_flow: LoginFlow,
    signed_out_afterwards,
):
    """One continuous flow, one login, one window: password visibility, sign
    in, the full two-factor dialog chain, and back to the authenticated app.

    Driven by ``login_credentials`` (resolved from the ``role`` fixture), not
    by a role-specific fixture, so this exact test runs unchanged for any role
    - only ``role`` needs to change. Only Platform Admin is exercised this
    phase; the other three roles stay configured but unexecuted.

    Read-only by design. ``Enable 2FA`` only requests a setup secret and opens
    the setup screen; two-factor authentication is switched on by
    ``Verify & Enable``, which is asserted but **never clicked** - doing so
    would lock a shared QA account behind an authenticator app.

    No dashboard/menu-specific automation happens here - the flow ends the
    moment the authenticated shell is confirmed. Role-specific dashboard
    validation is a separate, later task.
    """
    login_flow.exercise_password_visibility()
    login_flow.sign_in()
    login_flow.complete_two_factor_chain()
    login_flow.confirm_authenticated()
