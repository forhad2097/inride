"""Role, page-object and browser-session fixtures.

Window budget for a whole run: **two**.

* ``guest_session``  - one unauthenticated window, used by the login page suite.
* ``admin_session``  - one authenticated window, used by every access-validation
  suite.

pytest-playwright's ``page`` fixture is intentionally never used: it opens a new
browser context - a new visible window - for every test, which made the headed
demo flash a fresh window before each step.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, Page

from conftest import new_session
from config.roles import Credentials, Role, credentials_for
from pages.app_shell import AppShell
from pages.conversations_page import ConversationsPage
from pages.login_page import LoginPage
from utils.highlight import Highlighter
from utils.logger import get_logger

log = get_logger(__name__)


# --------------------------------------------------------------- roles
@pytest.fixture(scope="session")
def role() -> Role:
    """The role under test in this phase.

    Parametrise this fixture (or override it per test) when the later phases
    add Dealer Admin, User and Read-Only User.
    """
    return Role.PLATFORM_ADMIN


@pytest.fixture(scope="session")
def platform_admin() -> Credentials:
    return credentials_for(Role.PLATFORM_ADMIN)


# ----------------------------------------------- unauthenticated window
@pytest.fixture(scope="session")
def guest_session(browser: Browser, context_options: dict) -> Iterator[Page]:
    """One window for the pre-login validations."""
    yield from new_session(browser, context_options, "login-page-session")


@pytest.fixture
def login_page(guest_session: Page) -> Iterator[LoginPage]:
    page_object = LoginPage(guest_session)
    yield page_object
    Highlighter().restore_all(guest_session)


# ------------------------------------------------- authenticated window
@pytest.fixture(scope="session")
def admin_session(
    browser: Browser, context_options: dict, platform_admin: Credentials
) -> Iterator[AppShell]:
    """One authenticated window, shared by the read-only navigation tests.

    Justified because every test using it only *reads* the application - no
    test creates, edits or deletes data, so there is no state to leak. Each
    test still navigates to the page it needs, so the tests remain order
    independent.
    """
    for page in new_session(browser, context_options, "platform-admin-session"):
        shell = LoginPage(page).open().login(platform_admin)
        log.info("authenticated session ready for %s", platform_admin.role.value)
        yield shell


@pytest.fixture
def admin_shell(admin_session: AppShell) -> Iterator[AppShell]:
    """Per-test handle on the shared authenticated window, cleaned of any
    highlight left behind by the previous test."""
    yield admin_session
    Highlighter().restore_all(admin_session.page)


@pytest.fixture
def conversations_page(admin_shell: AppShell) -> ConversationsPage:
    return ConversationsPage(admin_shell.page)
