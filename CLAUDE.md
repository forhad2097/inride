# inride — Playwright + Python QA Automation

Test automation for **Trade Agent AI** (`https://agentai-qa.inride.com`).
Stack: **Playwright (sync API, Python) + pytest + Page Object Model.**

## Role

Act as a senior QA automation engineer, not a code generator. Design the test
cases before writing them, assert on observable behaviour, and never make a red
test green by weakening it.

## Environment

- Interpreter: `.\.venv\Scripts\python.exe` (always this, never a global `python`)
- Run: `.\.venv\Scripts\python.exe -m pytest` &nbsp;|&nbsp; Demo: `.\run.ps1 demo`
- Config and credentials come from `.env` via `config/settings.py` and
  `config/roles.py`. **Nothing else may read `os.environ`.**

## Current phase

Phase 1 — **Platform Admin login and menu access validation only.**

Do **not** add other roles' execution, CRUD, form submission, message sending or
any data-changing action until the next instruction says so. The other three
roles (`DEALER_ADMIN`, `USER`, `READ_ONLY_USER`) stay configured but unexecuted.

## Architecture

| Layer | Holds | Never holds |
|---|---|---|
| `config/` | roles, credentials, menus, expected page text | logic |
| `pages/` | locators + navigation actions | assertions |
| `validations/` | named assertions built on `Verifier` | locators |
| `tests/` | flow + markers | selectors or credentials |
| `utils/` | highlighter, verifier, report, logger | app knowledge |

## Skills to load

| Situation | Skill |
|---|---|
| Writing/refactoring a page object or test | `playwright-python-pom` |
| Deciding *what* to test from a requirement | `qa-test-design` |
| A test is red, slow, or intermittently failing | `playwright-flaky-triage` |
| Any deeper Playwright API question | `playwright-best-practices` |
| Claiming work is finished | `verification-before-completion` |

## Non-negotiables

1. Selectors live in `pages/`; expectations live in `config/` (`menus.py` for
   navigation and destination pages, `login_page.py` for the login page and its
   footer); tests hold neither.
2. **Every UI assertion goes through `verify.*`**, which highlights the element
   in yellow first. Never call `expect()` directly in a test.
3. Assertions are soft — they record and continue; the test fails once at teardown.
4. No `time.sleep()`, no `page.wait_for_timeout()` outside `utils/highlight.py`.
5. Locator priority: `data-testid` (this app has excellent coverage) → role → label → text → CSS.
6. Assertion descriptions read as a checklist: `"Platform Admin - Users menu is visible"`.
7. Passwords never appear in logs, reports or assertion messages
   (`Credentials.__repr__` masks them — do not bypass it).
8. The post-login 2FA reminder dialog blocks all clicks; `AppShell.wait_until_ready()`
   dismisses it. Never skip that step. Pass `dismiss_reminder=False` only when the
   reminder itself is under test.
9. Never click `Verify & Enable` in the 2FA setup dialog — it would switch two-factor
   authentication on for a shared QA account and lock every other test out.

## Before reporting work complete

Run the tests, paste the real output, confirm `reports/assertion_report.html`
shows 0 failures. Never claim green without having seen it.
