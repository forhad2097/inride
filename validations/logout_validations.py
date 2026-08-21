"""Profile-menu and sign-out assertions.

Expectations come from ``config/profile_menu.py``; locators come from
``pages/profile_menu.py``. Nothing here knows a selector.

Role handling is data-driven: each entry declares which roles may see it, so
``validate_role_dependent_items`` asserts *visible* or *not visible* from the
logged-in role without a single ``if role ==`` branch.
"""

from __future__ import annotations

import re

from config import profile_menu as copy
from config.roles import Credentials, Role
from config.settings import settings
from pages.login_page import LoginPage
from pages.profile_menu import ProfileMenu
from utils.logger import get_logger
from utils.verification import Verifier

log = get_logger(__name__)


class LogoutValidations:
    """Every assertion is named so the report reads as a checklist."""

    def __init__(self, verify: Verifier, profile_menu: ProfileMenu, role: Role) -> None:
        self.verify = verify
        self.page_object = profile_menu
        self.role = role
        self.prefix = f"{role.display_name} - Profile Menu"

    # ============================================ menu is open
    def validate_menu_opened(self) -> None:
        self.verify.visible(
            self.page_object.avatar,
            f"{self.role.display_name} - Avatar is visible in the top-right corner",
        )
        self.verify.visible(
            self.page_object.menu, f"{self.prefix} is displayed after clicking the avatar"
        )
        self.verify.visible(
            self.page_object.account_name, f"{self.prefix} shows the account name"
        )

    # ==================================== logged-in email matches
    def validate_logged_in_email(self, credentials: Credentials) -> None:
        """The email in the dropdown must be the one this session signed in with.

        Compared against the credentials actually used, never a hardcoded
        address, so this holds for whichever role the suite is pointed at.
        """
        expected = credentials.username
        self.verify.visible(
            self.page_object.account_email, f"{self.prefix} shows the logged-in email"
        )
        self.verify.has_text(
            self.page_object.account_email,
            expected,
            f"{self.prefix} email matches the account used to log in ('{expected}')",
        )

    # ========================================= the standard entries
    def validate_common_items(self) -> None:
        """Edit Profile, Change Password and 2FA Setup - one assertion each."""
        for entry in copy.COMMON_ITEMS:
            self._validate_visible(entry)

    # ============================== role-dependent entries (data-driven)
    def validate_role_dependent_items(self) -> None:
        """Assert each role-gated entry is shown *or* hidden, per the role.

        For a role that may see it, absence fails. For a role that may not,
        presence fails - the check is never just "does it exist".
        """
        for entry in copy.ROLE_DEPENDENT_ITEMS:
            allowed = ", ".join(r.display_name for r in (entry.visible_for or ()))
            if entry.expected_for(self.role):
                self._validate_visible(entry)
                self.verify.record_info(
                    f"{self.prefix} '{entry.label}' is role-gated and "
                    f"{self.role.display_name} is permitted",
                    f"visible only for: {allowed}",
                )
            else:
                self.verify.has_count(
                    self.page_object.item(entry),
                    0,
                    f"{self.prefix} '{entry.label}' is NOT available to "
                    f"{self.role.display_name}",
                )
                self.verify.record_info(
                    f"{self.prefix} '{entry.label}' is correctly withheld from "
                    f"{self.role.display_name}",
                    f"visible only for: {allowed}",
                )

    # ================================================ the logout entry
    def validate_logout_item(self) -> None:
        self._validate_visible(copy.LOGOUT)

    # ============================================ after signing out
    def validate_back_on_login_page(self, login_page: LoginPage) -> None:
        """Signed out means: the login endpoint, and a usable login form.

        Only the path is asserted - the host comes from the configured base
        URL, so this holds on Local, QA, Staging and Production alike.

        Deliberately minimal: the full login page suite is a separate flow and
        is not repeated here.
        """
        expected_url = re.compile(
            re.escape(settings.url.rstrip("/")) + re.escape(copy.LOGIN_PATH) + r"/?$"
        )
        self.verify.url_is(
            login_page.page,
            expected_url,
            f"{self.role.display_name} - Logout redirects to the login endpoint "
            f"('{copy.LOGIN_PATH}')",
        )
        self.verify.custom(
            f"{self.role.display_name} - Landing path after logout is "
            f"'{copy.LOGIN_PATH}'",
            lambda: _assert_path(login_page.path, copy.LOGIN_PATH),
            expected=f"path == {copy.LOGIN_PATH!r}",
            actual=login_page.path,
        )
        self.verify.visible(
            login_page.login_title,
            f"{self.role.display_name} - 'Log In' is visible again after logout",
        )
        self.verify.visible(
            login_page.email_input,
            f"{self.role.display_name} - Login form is displayed again after logout "
            f"(email field)",
        )
        self.verify.visible(
            login_page.password_input,
            f"{self.role.display_name} - Login form is displayed again after logout "
            f"(password field)",
        )
        self.verify.visible(
            login_page.login_button,
            f"{self.role.display_name} - Login button is available again after logout",
        )

    def validate_session_is_over(self, login_page: LoginPage) -> None:
        """The authenticated shell is genuinely gone, not just navigated away."""
        self.verify.has_count(
            login_page.page.get_by_test_id("button-profile-menu"),
            0,
            f"{self.role.display_name} - Avatar is no longer present once signed out",
        )

    # --- internals --------------------------------------------------
    def _validate_visible(self, entry: copy.ProfileMenuItem) -> None:
        locator = self.page_object.item(entry)
        self.verify.visible(locator, f"{self.prefix} '{entry.label}' is visible")
        self.verify.has_text(
            locator,
            entry.label,
            f"{self.prefix} '{entry.label}' label text is exactly '{entry.label}'",
        )
        if entry.deviates:
            self.verify.record_info(
                f"{self.prefix} '{entry.label}' wording differs from the requirement "
                f"document",
                f"requirement asked for '{entry.spec_label}', "
                f"application renders '{entry.label}'",
            )


def _assert_path(actual: str, expected: str) -> None:
    assert actual.rstrip("/") == expected.rstrip("/"), (
        f"expected path {expected!r}, landed on {actual!r}"
    )
