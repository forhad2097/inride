"""The complete login journey, reusable from any test.

Steps are exposed individually so a suite can run them in isolation for
triage, and ``run()`` performs the whole journey end to end.

Role-driven: the flow is built from a ``Role`` plus its ``Credentials``, never
from a role-specific fixture, so pointing it at Dealer Admin, User or
Read-Only User later runs this exact code with no edit.

Read-only by design. ``Enable 2FA`` only requests a setup secret and opens the
setup screen; two-factor authentication is switched on by ``Verify & Enable``,
which is asserted but **never clicked** - doing so would lock a shared QA
account behind an authenticator app.
"""

from __future__ import annotations

from config.roles import Credentials, Role
from pages.app_shell import AppShell
from pages.login_page import LoginPage
from pages.two_factor import TwoFactorReminderDialog
from utils.logger import get_logger
from utils.verification import Verifier
from validations.login_validations import LoginPageValidations
from validations.navigation_validations import NavigationValidations
from validations.two_factor_validations import TwoFactorValidations

log = get_logger(__name__)


class LoginFlow:
    """Login page validation, sign-in, and the post-login two-factor chain."""

    def __init__(
        self,
        verify: Verifier,
        login_page: LoginPage,
        role: Role,
        credentials: Credentials,
    ) -> None:
        self.verify = verify
        self.login_page = login_page
        self.role = role
        self.credentials = credentials

        self.page_validations = LoginPageValidations(verify, login_page, role)
        self.two_factor = TwoFactorValidations(verify, role)
        self.shell: AppShell | None = None

    # --- individual steps -------------------------------------------
    def open_login_page(self) -> "LoginFlow":
        self.login_page.open()
        return self

    def validate_login_page_ui(self) -> "LoginFlow":
        """Branding and every control on the form."""
        self.page_validations.validate_branding()
        self.page_validations.validate_login_form()
        return self

    def validate_footer(self) -> "LoginFlow":
        """Footer logo, Legal, Contact Info, social icons and the copyright."""
        self.page_validations.validate_footer()
        return self

    def exercise_password_visibility(self) -> "LoginFlow":
        """Type the credentials, then show and hide the password.

        The typed value is compared at every stage but never reported.
        """
        password = self.credentials.password
        self.login_page.fill_credentials(self.credentials)
        self.page_validations.validate_password_is_masked(
            password, stage="after it is typed in"
        )

        self.login_page.show_password()
        self.page_validations.validate_password_is_revealed(password)
        self.page_validations.validate_toggle_offers_hide()

        self.login_page.hide_password()
        self.page_validations.validate_password_is_masked(
            password, stage="after hiding it again"
        )
        self.page_validations.validate_toggle_offers_show()
        return self

    def sign_in(self) -> AppShell:
        """Submit the form, leaving the reminder popup up to be asserted."""
        self.shell = self.login_page.submit(dismiss_reminder=False)
        NavigationValidations(self.verify, self.shell, self.role).validate_logged_in()
        return self.shell

    def complete_two_factor_chain(self) -> AppShell:
        """The three post-login dialogs, ending back in the authenticated app.

        reminder -> security settings -> setup -> Cancel -> close.
        """
        shell = self._require_shell()

        # --- first popup: "Protect your account with 2FA" ---
        reminder = TwoFactorReminderDialog(shell.page).wait_until_shown()
        self.two_factor.validate_reminder_dialog(reminder)

        # --- "Open Security Settings", not "Maybe Later" ---
        settings_dialog = reminder.open_security_settings()
        self.two_factor.validate_settings_dialog(settings_dialog)
        self.two_factor.validate_close_control(settings_dialog)

        # --- "Enable 2FA" opens the setup screen ---
        settings_dialog.enable_two_factor()
        self.two_factor.validate_setup_dialog(settings_dialog)
        self.two_factor.validate_qr_code(settings_dialog)
        self.two_factor.validate_manual_code(settings_dialog)
        self.two_factor.validate_token_input(settings_dialog)
        self.two_factor.validate_setup_buttons(settings_dialog)

        # --- Cancel returns to the settings screen, account unchanged ---
        settings_dialog.cancel_setup()
        self.two_factor.validate_setup_closed_and_settings_restored(settings_dialog)

        # --- the X closes the settings popup ---
        settings_dialog.close()
        self.two_factor.validate_settings_closed(settings_dialog)
        self.two_factor.validate_reminder_closed(reminder)
        return shell

    def confirm_authenticated(self) -> AppShell:
        shell = self._require_shell()
        NavigationValidations(self.verify, shell, self.role).validate_logged_in()
        self.verify.record_info(
            f"{self.role.display_name} - Application state after completing the login "
            f"and two-factor flow",
            shell.current_url,
        )
        return shell

    # --- whole journeys ---------------------------------------------
    def run(self) -> AppShell:
        """The complete login flow: page UI, footer, password visibility,
        sign-in, the full two-factor chain, and the authenticated shell."""
        log.info("running the full login flow as %s", self.role.value)
        self.open_login_page()
        self.validate_login_page_ui()
        self.validate_footer()
        self.exercise_password_visibility()
        self.sign_in()
        self.complete_two_factor_chain()
        return self.confirm_authenticated()

    def sign_in_only(self) -> AppShell:
        """Authenticate with no login page assertions and no 2FA walkthrough.

        For future feature tests that need a session, not a login report:

            shell = LoginFlow(...).sign_in_only()   # login
            ...                                    # the scenario under test
            LogoutFlow(...).run()                  # logout
        """
        log.info("signing in as %s (no login page assertions)", self.role.value)
        self.login_page.open()
        self.shell = self.login_page.login(self.credentials)  # dismisses the reminder
        return self.shell

    def ensure_authenticated(self) -> AppShell:
        """Return an authenticated shell, signing in only if the window is not
        already signed in.

        Lets a logout test stand on its own - it signs in when run alone, and
        reuses the session when a login test has just run in the same window.
        """
        shell = AppShell(self.login_page.page)
        try:
            shell.profile_menu.wait_for(state="visible", timeout=5000)
        except Exception:  # noqa: BLE001 - not signed in yet is the normal case
            return self.sign_in_only()

        log.info("window is already authenticated - reusing the session")
        shell.dismiss_two_factor_reminder()
        self.shell = shell
        return shell

    # --- internals --------------------------------------------------
    def _require_shell(self) -> AppShell:
        if self.shell is None:
            raise RuntimeError(
                "LoginFlow: sign_in() must run before the post-login steps."
            )
        return self.shell
