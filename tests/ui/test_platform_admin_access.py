"""Platform Admin login and menu access validation.

Read-only: this suite opens pages and asserts what is displayed. It creates,
edits and deletes nothing.

| Case                                            | Priority | Covers        |
|-------------------------------------------------|----------|---------------|
| platform admin can log in                       | P0       | PA-LOGIN-01   |
| all 14 expected main menus are visible          | P0       | PA-MENU-01    |
| Conversations exposes the Email and SMS submenus| P0       | PA-CONV-01    |
| Dealer Profile page shows its header and text   | P0       | PA-DEALER-01  |
| Users page shows its header and text            | P0       | PA-USERS-01   |
| every remaining menu opens and shows its header | P1       | PA-PAGE-xx    |
"""

import pytest

from config.menus import CONVERSATIONS, DEALER_PROFILE, USERS, menus_for, secondary_menus
from config.roles import Role
from pages.app_shell import AppShell
from pages.conversations_page import ConversationsPage
from utils.verification import Verifier
from validations.navigation_validations import NavigationValidations
from validations.page_validations import PageValidations

ROLE_UNDER_TEST = Role.PLATFORM_ADMIN
SECONDARY_MENUS = secondary_menus(ROLE_UNDER_TEST)


@pytest.fixture
def navigation(verify: Verifier, admin_shell: AppShell, role: Role) -> NavigationValidations:
    return NavigationValidations(verify, admin_shell, role)


@pytest.fixture
def pages(verify: Verifier, admin_shell: AppShell, role: Role) -> PageValidations:
    return PageValidations(verify, admin_shell, role)


@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.login
def test_platform_admin_can_log_in(navigation: NavigationValidations):
    navigation.validate_logged_in()


@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.menu
def test_platform_admin_sees_all_expected_main_menus(
    navigation: NavigationValidations, role: Role
):
    expected = menus_for(role)

    navigation.validate_menu_count(expected)
    navigation.validate_all_menus(expected)


@pytest.mark.smoke
@pytest.mark.menu
def test_conversations_menu_exposes_email_and_text_submenus(
    admin_shell: AppShell,
    conversations_page: ConversationsPage,
    navigation: NavigationValidations,
    pages: PageValidations,
):
    admin_shell.open_menu(CONVERSATIONS)

    pages.validate_page_loaded(CONVERSATIONS)
    for submenu in CONVERSATIONS.submenus:
        navigation.validate_submenu(conversations_page, submenu)


@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.menu
def test_dealer_profile_page_shows_expected_content(
    admin_shell: AppShell, pages: PageValidations
):
    admin_shell.open_menu(DEALER_PROFILE)

    pages.validate(DEALER_PROFILE)


@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.menu
def test_users_page_shows_expected_content(admin_shell: AppShell, pages: PageValidations):
    admin_shell.open_menu(USERS)

    pages.validate(USERS)


@pytest.mark.regression
@pytest.mark.menu
@pytest.mark.parametrize("menu_item", SECONDARY_MENUS, ids=lambda m: m.key)
def test_remaining_menu_opens_and_shows_its_primary_header(
    admin_shell: AppShell, pages: PageValidations, verify: Verifier, menu_item
):
    try:
        admin_shell.open_menu(menu_item)
    except Exception as exc:  # noqa: BLE001
        # Record and stop this menu's checks; the other menus are separate
        # test cases and still run.
        verify.record_failure(
            f"{ROLE_UNDER_TEST.display_name} - {menu_item.label} menu could not be opened",
            f"{type(exc).__name__}: {exc}",
            page=admin_shell.page,
        )
        return

    pages.validate(menu_item)
