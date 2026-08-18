---
name: playwright-python-pom
description: Use when writing, refactoring or reviewing Playwright tests in Python for the inride project - covers Page Object Model layout, locator priority, web-first assertions, pytest fixtures/markers, test data, and the exact commands to run the suite. Read this BEFORE creating any page class or test file.
---

# Playwright + Python Page Object Model

Authoritative conventions for this repo. Deviating from them is a review failure.

## The Iron Rules

1. **No selector strings inside a test file.** Every locator lives in a page or component class.
2. **No assertions inside page-object action methods.** Actions do; tests assert. (Exception: an explicit `expect_*` / `assert_*` method the test calls on purpose.)
3. **No `time.sleep()`. No `wait_for_timeout()`.** Ever. Use web-first assertions — they auto-retry.
4. **Every page method does one thing** and is named for user intent (`submit_order`, not `click_button_3`).
5. **Navigation returns the next page object.** `login()` returns `InventoryPage`, so the test reads like a user journey.

## Directory Map

```
config/settings.py      # env-driven config (base_url, credentials, timeouts)
pages/base_page.py      # BasePage: shared navigation + waits
pages/*_page.py         # one class per page, suffix _page.py
components/*.py         # reusable widgets scoped to a container Locator
tests/ui/test_*.py      # UI specs; import page objects only
tests/api/test_*.py     # APIRequestContext specs
tests/conftest.py       # page-object fixtures
data/                   # test data + factories
utils/                  # logger, generic helpers
reports/                # HTML report, traces, videos (gitignored)
```

## Page Class Template

```python
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Locators are declared once, in __init__, and never rebuilt inline.
        self.username_input: Locator = page.get_by_placeholder("Username")
        self.password_input: Locator = page.get_by_placeholder("Password")
        self.login_button: Locator = page.get_by_role("button", name="Login")
        self.error_message: Locator = page.locator('[data-test="error"]')

    def open(self) -> "LoginPage":
        self.navigate(self.PATH)
        return self

    def login(self, username: str, password: str) -> "InventoryPage":
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        from pages.inventory_page import InventoryPage
        return InventoryPage(self.page)

    def expect_error(self, text: str) -> None:
        expect(self.error_message).to_contain_text(text)
```

## Locator Priority (top wins)

| Rank | API | Use for |
|---|---|---|
| 1 | `get_by_role("button", name="Login")` | anything with an accessible name |
| 2 | `get_by_label()`, `get_by_placeholder()` | form fields |
| 3 | `get_by_text()`, `get_by_title()` | static copy |
| 4 | `get_by_test_id()` | when no semantic handle exists |
| 5 | `locator("css=...")` | last resort, document why |

Never: XPath by position, `nth-child` chains, auto-generated class names, text that changes with locale.

Scope instead of guessing: `self.cart.get_by_role("listitem").filter(has_text="Backpack")`.

## Assertions — web-first only

```python
expect(page).to_have_url(re.compile(r"/inventory"))
expect(locator).to_be_visible()
expect(locator).to_have_text("Products")
expect(locator).to_have_count(6)
expect(locator).to_have_attribute("href", "/cart")
```

Banned patterns:
```python
assert locator.is_visible()          # no retry -> flaky
assert locator.text_content() == "X" # no retry -> flaky
page.wait_for_timeout(2000)          # arbitrary sleep
```
`is_visible()` returns a snapshot; `expect(...).to_be_visible()` polls until the timeout. Use the second one.

## Fixtures

Page objects come from fixtures in `tests/conftest.py`, never constructed inline in a test:

```python
@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)
```

Auth state is reused via `storage_state` (see `conftest.py`), not by logging in through the UI in every test.

## Markers

Declared in `pytest.ini`. Tag every test with at least one:
`@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.critical`, `@pytest.mark.negative`, `@pytest.mark.api`.

## Commands

```bash
.venv/Scripts/python.exe -m pytest                    # full suite, headless
.venv/Scripts/python.exe -m pytest -m smoke           # smoke only
.venv/Scripts/python.exe -m pytest --headed --slowmo 400   # demo mode
.venv/Scripts/python.exe -m pytest -n 4               # parallel
.venv/Scripts/python.exe -m pytest --tracing on       # traces into reports/
playwright show-trace reports/traces/<name>.zip       # inspect a failure
```

## Test File Template

```python
import pytest
from pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.critical
def test_valid_user_reaches_inventory(login_page: LoginPage, standard_user):
    inventory = login_page.open().login(standard_user.username, standard_user.password)
    inventory.expect_loaded()
```

One behaviour per test. The name states the expected behaviour, not the steps.

## Before Saying "Done"

- [ ] Test run, output pasted, all green
- [ ] Ran the new test twice (`--count 2`) — no flake
- [ ] No sleeps, no raw `assert` on locator state
- [ ] No selectors leaked into `tests/`
- [ ] Markers applied

Deeper reference for any Playwright topic: the `playwright-best-practices` skill (TypeScript examples, but the API surface and reasoning are identical).
