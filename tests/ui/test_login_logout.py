"""Login + Logout suite - the two flows running together, end to end.

    Login Test  ->  full login flow  ->  Platform Admin  ->  full 2FA chain
                ->  authenticated application state
    Logout Test ->  full logout flow ->  login page

The two tests are separate cases and the two flows are separate modules
(``flows/login_flow.py``, ``flows/logout_flow.py``). They run in one window,
in this order, but neither depends on the other's *code*: the logout test
signs in for itself when run alone, and reuses the session when the login test
has just left one behind.

The role is a single variable - the ``role`` fixture in ``tests/conftest.py``.
Point it at another Role and both flows run unchanged for that role.

| Case                                             | Priority | Covers      |
|--------------------------------------------------|----------|-------------|
| full login flow signs the role in                | P0       | LOGIN-01..28, 2FA-01..13 |
| full logout flow returns to the login page       | P0       | LOGOUT-01..12 |
"""

import pytest
from playwright.sync_api import Page

from config.roles import Credentials, Role
from flows.login_flow import LoginFlow
from flows.logout_flow import LogoutFlow
from pages.app_shell import AppShell
from pages.login_page import LoginPage
from utils.logger import get_logger
from utils.verification import Verifier

log = get_logger(__name__)


@pytest.fixture
def login_flow(
    verify: Verifier, login_page: LoginPage, role: Role, login_credentials: Credentials
) -> LoginFlow:
    return LoginFlow(verify, login_page, role, login_credentials)


@pytest.fixture
def authenticated_shell(login_flow: LoginFlow) -> AppShell:
    """An authenticated window for the logout test.

    Reuses the session the login test left behind; signs in on its own when the
    logout test is run alone. That is what keeps the logout flow independent of
    whatever ran before it.
    """
    return login_flow.ensure_authenticated()


@pytest.fixture
def signed_out_afterwards(guest_session: Page):
    """Leave the shared window signed out however the test ended."""
    yield
    try:
        guest_session.context.clear_cookies()
        guest_session.evaluate(
            "() => { window.localStorage.clear(); window.sessionStorage.clear(); }"
        )
        log.info("guest window returned to its signed-out state")
    except Exception as exc:  # noqa: BLE001 - cleanup must never fail a green test
        log.debug("could not reset the guest window: %s", exc)


# ------------------------------------------------------------ 1. login
@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.login
@pytest.mark.two_factor
def test_login_flow_signs_the_role_in(login_flow: LoginFlow):
    """The complete login flow: page UI, footer, password show/hide, sign-in,
    the full two-factor dialog chain, and the authenticated application."""
    login_flow.run()


# ----------------------------------------------------------- 2. logout
@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.logout
def test_logout_flow_returns_to_the_login_page(
    authenticated_shell: AppShell,
    verify: Verifier,
    role: Role,
    login_credentials: Credentials,
    signed_out_afterwards,
):
    """The complete logout flow, starting from an authenticated application.

    Avatar -> logged-in email -> Edit Profile / Change Password / 2FA Setup ->
    role-gated Onboard Telgorithm -> Logout -> login endpoint -> login form.
    """
    LogoutFlow(verify, authenticated_shell, role, login_credentials).run()
