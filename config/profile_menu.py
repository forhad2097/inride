"""Expected content of the avatar / profile dropdown, and who may see it.

Data only. ``pages/profile_menu.py`` knows *how* to open and locate the menu;
this module records *what* must be in it and *which roles* may see each entry.

Visibility is expressed as data (``visible_for``), not as an ``if role ==``
branch in a test, so adding a role later is an edit here and nothing else.

Where the requirement document used different wording than the application
renders, ``spec_label`` records the requested wording. The suite asserts the
**actual** label and reports the deviation rather than silently passing.
"""

from __future__ import annotations

from dataclasses import dataclass

from config.roles import Role


@dataclass(frozen=True)
class ProfileMenuItem:
    """One entry in the avatar dropdown."""

    key: str
    #: the label the application renders today
    label: str
    test_id: str
    #: wording used in the requirement document, when it differs from the UI
    spec_label: str | None = None
    #: roles that must see this entry; ``None`` means every role
    visible_for: tuple[Role, ...] | None = None

    @property
    def deviates(self) -> bool:
        return self.spec_label is not None and self.spec_label != self.label

    def expected_for(self, role: Role) -> bool:
        """Whether ``role`` must be able to see this entry."""
        return self.visible_for is None or role in self.visible_for


EDIT_PROFILE = ProfileMenuItem(
    key="edit_profile",
    label="Edit Profile",
    test_id="button-edit-profile",
)

CHANGE_PASSWORD = ProfileMenuItem(
    key="change_password",
    label="Change Password",
    test_id="button-change-password",
)

# The requirement calls this "Two-Factor Setup"; the application labels it
# "2FA Setup" and the test id still says security-settings.
TWO_FACTOR_SETUP = ProfileMenuItem(
    key="two_factor_setup",
    label="2FA Setup",
    test_id="button-security-settings",
    spec_label="Two-Factor Setup",
)

# Role-dependent. The requirement calls this "Onboarding Algorithm"; the
# application renders "Onboard Telgorithm" - Telgorithm being the messaging
# compliance provider - so the requirement's wording looks like a mishearing
# rather than a defect. Asserted as rendered, deviation reported.
ONBOARD_TELGORITHM = ProfileMenuItem(
    key="onboard_telgorithm",
    label="Onboard Telgorithm",
    test_id="button-onboard-telgorithm",
    spec_label="Onboarding Algorithm",
    visible_for=(Role.PLATFORM_ADMIN, Role.DEALER_ADMIN),
)

# The requirement calls this "Logout"; the application renders "Log out".
LOGOUT = ProfileMenuItem(
    key="logout",
    label="Log out",
    test_id="button-logout",
    spec_label="Logout",
)


#: entries every authenticated role must see
COMMON_ITEMS: tuple[ProfileMenuItem, ...] = (
    EDIT_PROFILE,
    CHANGE_PASSWORD,
    TWO_FACTOR_SETUP,
)

#: entries whose visibility depends on the logged-in role
ROLE_DEPENDENT_ITEMS: tuple[ProfileMenuItem, ...] = (ONBOARD_TELGORITHM,)

#: every entry, in the order the menu renders them
ALL_ITEMS: tuple[ProfileMenuItem, ...] = COMMON_ITEMS + ROLE_DEPENDENT_ITEMS + (LOGOUT,)


def items_expected_for(role: Role) -> tuple[ProfileMenuItem, ...]:
    return tuple(item for item in ALL_ITEMS if item.expected_for(role))


def items_hidden_for(role: Role) -> tuple[ProfileMenuItem, ...]:
    return tuple(item for item in ALL_ITEMS if not item.expected_for(role))


#: where the application lands once the session ends. Only the path is fixed;
#: the host comes from ``settings.url``, so Local/QA/Staging/Prod all work.
LOGIN_PATH = "/login"
