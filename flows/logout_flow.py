"""The complete sign-out journey, reusable from any test.

Standalone by design. It assumes only that:

1. a user is authenticated,
2. the authenticated application is open in the window, and
3. the avatar is reachable in the top bar.

It never assumes *how* the session started or what was exercised in between,
so any future test can end with it:

    shell = LoginFlow(...).sign_in_only()
    ...                                  # create a dealer, test a module, ...
    LogoutFlow(verify, shell, role, credentials).run()

Nothing about logging in lives here, and nothing about logging out lives in
``LoginFlow`` or ``LoginPage``.
"""

from __future__ import annotations

from config.profile_menu import LOGOUT
from config.roles import Credentials, Role
from pages.app_shell import AppShell
from pages.login_page import LoginPage
from pages.profile_menu import ProfileMenu
from utils.logger import get_logger
from utils.verification import Verifier
from validations.logout_validations import LogoutValidations

log = get_logger(__name__)


class LogoutFlow:
    """Open the profile menu, validate it, sign out, land on the login page."""

    def __init__(
        self,
        verify: Verifier,
        shell: AppShell,
        role: Role,
        credentials: Credentials,
    ) -> None:
        self.verify = verify
        self.role = role
        self.credentials = credentials
        self.profile_menu = ProfileMenu(shell.page)
        self.validations = LogoutValidations(verify, self.profile_menu, role)
        self.login_page: LoginPage | None = None

    # --- individual steps -------------------------------------------
    def open_profile_menu(self) -> "LogoutFlow":
        """Click the avatar in the top-right corner and confirm the dropdown."""
        self.profile_menu.open()
        self.validations.validate_menu_opened()
        return self

    def validate_logged_in_email(self) -> "LogoutFlow":
        """The dropdown must show the address this session signed in with."""
        self.validations.validate_logged_in_email(self.credentials)
        return self

    def validate_menu_items(self) -> "LogoutFlow":
        """Edit Profile, Change Password, 2FA Setup, then the role-gated
        entries, then Logout."""
        self.validations.validate_common_items()
        self.validations.validate_role_dependent_items()
        self.validations.validate_logout_item()
        return self

    def sign_out(self) -> LoginPage:
        """Click Logout and wait for the login page to come back."""
        self.login_page = self.profile_menu.logout(LOGOUT)
        return self.login_page

    def validate_signed_out(self) -> LoginPage:
        """Login endpoint, login form, and the session genuinely gone.

        Deliberately minimal - the full login page suite belongs to
        ``LoginFlow`` and is not repeated here.
        """
        login_page = self._require_login_page()
        self.validations.validate_back_on_login_page(login_page)
        self.validations.validate_session_is_over(login_page)
        return login_page

    # --- whole journey ----------------------------------------------
    def run(self) -> LoginPage:
        """Avatar -> email -> menu items -> role gate -> Logout -> login page."""
        log.info("running the logout flow as %s", self.role.value)
        self.open_profile_menu()
        self.validate_logged_in_email()
        self.validate_menu_items()
        self.sign_out()
        return self.validate_signed_out()

    # --- internals --------------------------------------------------
    def _require_login_page(self) -> LoginPage:
        if self.login_page is None:
            raise RuntimeError("LogoutFlow: sign_out() must run before validation.")
        return self.login_page
