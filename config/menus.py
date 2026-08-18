"""Expected navigation structure, per role.

This module holds *navigation* facts only (label, locator, URL path) and the
*expected page content* for each destination. Both are data, so adding a menu,
a role, or a new page assertion later means editing this file - not a test.

``page_texts`` deliberately carries the text exactly as the application renders
it today. Where the requirement document used different wording, ``spec_text``
records what the requirement asked for, so a deviation is visible rather than
silently absorbed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from config.roles import Role


@dataclass(frozen=True)
class ExpectedText:
    """One text assertion on a page."""

    value: str
    label: str
    #: wording used in the requirement document, when it differs from the UI
    spec_text: str | None = None
    #: substring match instead of exact match
    partial: bool = False


@dataclass(frozen=True)
class SubMenuItem:
    key: str
    label: str
    test_id: str
    spec_name: str | None = None


@dataclass(frozen=True)
class MenuItem:
    """A left-navigation entry and what its destination page must show."""

    key: str
    label: str
    test_id: str
    #: URL path the application lands on when the menu is opened
    path: str
    #: primary page header text; ``None`` when the page renders no <h1>
    heading: str | None = None
    #: extra text assertions for this page
    page_texts: tuple[ExpectedText, ...] = ()
    submenus: tuple[SubMenuItem, ...] = ()


# ---------------------------------------------------------------------------
# Platform Admin
# ---------------------------------------------------------------------------

CONVERSATIONS = MenuItem(
    key="conversations",
    label="Conversations",
    test_id="link-conversations",
    path="/",
    heading=None,  # the conversations workspace renders tabs, not an <h1>
    submenus=(
        SubMenuItem(key="email", label="Email", test_id="tab-email"),
        # The requirement calls this submenu "Text"; the application labels it "SMS".
        SubMenuItem(key="sms", label="SMS", test_id="tab-sms", spec_name="Text"),
    ),
)

DEALER_PROFILE = MenuItem(
    key="dealer_profile",
    label="Dealer Profile",
    test_id="link-dealer-profile",
    path="/tenants",
    heading="Dealers",
    page_texts=(
        ExpectedText(
            value="Manage dealer organizations",
            label="Dealer Profile page description",
            spec_text="Manage Dealer Organization",
        ),
    ),
)

USERS = MenuItem(
    key="users",
    label="Users",
    test_id="link-users",
    path="/users",
    heading="Users",
    page_texts=(
        ExpectedText(
            value="Manage user accounts and permissions",
            label="Users page description",
            spec_text="Manage Users / Account & Permission",
        ),
    ),
)

PLATFORM_ADMIN_MENUS: tuple[MenuItem, ...] = (
    CONVERSATIONS,
    DEALER_PROFILE,
    USERS,
    MenuItem(
        key="customer_list",
        label="Customer List",
        test_id="link-customer-list",
        path="/leads",
        heading="Customer List",
        page_texts=(ExpectedText("Manage and track customers", "Customer List page description"),),
    ),
    MenuItem(
        key="campaigns",
        label="Campaigns",
        test_id="link-campaigns",
        path="/cadences",
        heading="Campaigns",
        page_texts=(ExpectedText("Manage workflow campaigns", "Campaigns page description"),),
    ),
    MenuItem(
        key="campaign_steps",
        label="Campaign Steps",
        test_id="link-campaign-steps",
        path="/cadence-steps",
        heading="Campaign Steps",
    ),
    MenuItem(
        key="template_variants",
        label="Template Variants",
        test_id="link-template-variants",
        path="/template-variants",
        heading="Template Variants",
    ),
    MenuItem(
        key="email_templates",
        label="Email Templates",
        test_id="link-email-templates",
        path="/email-templates",
        heading="Email Templates",
    ),
    MenuItem(
        key="knowledge_base",
        label="Knowledge Base",
        test_id="link-knowledge-base",
        path="/knowledge-base",
        heading="Knowledge Base",
    ),
    MenuItem(
        key="reports",
        label="Reports",
        test_id="link-reports",
        path="/reports",
        heading="Reports",
    ),
    MenuItem(
        key="automation_sequences",
        label="Automation Sequences",
        test_id="link-automation-sequences",
        path="/automation-sequences",
        # the menu reads "Automation Sequences"; the page header reads "Sequences"
        heading="Sequences",
    ),
    MenuItem(
        key="dealer_sso",
        label="Dealer SSO",
        test_id="link-dealer-sso",
        path="/dealer-sso",
        heading="Dealer SSO",
    ),
    MenuItem(
        key="push_notifications",
        label="Push Notifications",
        test_id="link-push-notifications",
        path="/notification",
        heading="Push Notification Preferences",
    ),
    MenuItem(
        key="value_adjustments",
        label="Value Adjustments",
        test_id="link-value-adjustments",
        path="/tenant-value-adjustments",
        heading="Value Adjustments",
    ),
)


# ---------------------------------------------------------------------------
# Registry - other roles are wired in here as their automation is added.
# ---------------------------------------------------------------------------

MENUS_BY_ROLE: dict[Role, tuple[MenuItem, ...]] = {
    Role.PLATFORM_ADMIN: PLATFORM_ADMIN_MENUS,
    # Role.DEALER_ADMIN: DEALER_ADMIN_MENUS,      # future phase
    # Role.USER: USER_MENUS,                      # future phase
    # Role.READ_ONLY_USER: READ_ONLY_USER_MENUS,  # future phase
}


def menus_for(role: Role) -> tuple[MenuItem, ...]:
    if role not in MENUS_BY_ROLE:
        raise KeyError(
            f"No expected menus configured for {role.value}. "
            f"Add them to MENUS_BY_ROLE in config/menus.py."
        )
    return MENUS_BY_ROLE[role]


def menu(role: Role, key: str) -> MenuItem:
    for item in menus_for(role):
        if item.key == key:
            return item
    raise KeyError(f"{role.value} has no menu with key {key!r}")


def secondary_menus(role: Role) -> tuple[MenuItem, ...]:
    """Menus beyond the three that have their own dedicated validations."""
    dedicated = {CONVERSATIONS.key, DEALER_PROFILE.key, USERS.key}
    return tuple(m for m in menus_for(role) if m.key not in dedicated)
