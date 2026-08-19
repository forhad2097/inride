# inride — Project Handover

> Complete context for continuing this work in a new environment.
> Paste this file into a fresh session and the assistant has everything it needs.

---

## 1. What this project is

QA test automation for **Trade Agent AI**, a web application for automotive dealers.

| | |
|---|---|
| **Application under test** | `https://agentai-qa.inride.com` (QA environment) |
| **Repository** | `https://github.com/forhad2097/inride` |
| **Local path** | `D:\inride` |
| **Owner** | forhad2097 |
| **This repo contains** | test automation only — **not** the application source |

---

## 2. Technology stack

| Layer | Tool | Version |
|---|---|---|
| Language | Python | 3.14.4 |
| Browser automation | **Playwright** (sync API) | 1.62.0 |
| Test runner | **pytest** | 9.1.1 |
| Playwright ↔ pytest bridge | pytest-playwright | 0.9.0 |
| HTML report | pytest-html | 4.2.0 |
| Parallel execution | pytest-xdist | 3.8.0 |
| Flake checking (`--count`) | pytest-repeat | 0.9.4 |
| Config / secrets | python-dotenv | 1.2.3 |
| Test data | Faker | 40.36.0 |

**Design pattern:** Page Object Model, split into four layers.

No BDD framework (Cucumber/Behave) and no Robot Framework. The "framework" parts —
highlighting, soft assertions, reporting — are custom code in `utils/`.

---

## 3. Current phase and scope

**Phase 1 — Platform Admin login and menu access validation. Read-only.**

### Done
- Login page: branding, tagline, form fields, SSO/Google buttons, dynamic footer
- Platform Admin login
- All 14 main menus asserted individually
- Conversations → Email / SMS submenus
- Dealer Profile page content
- Users page content
- Remaining 11 menus opened, primary header asserted (one parametrised test each)

### Deliberately NOT done (waiting for the next instruction)
- Dealer Admin, User, Read-Only User login — **configured but never executed**
- Role-to-role permission comparison
- Any create / update / delete
- Form submission, message or email sending
- API response validation
- Negative login cases

**Result: 18 tests, 133 validations, all passing.**

---

## 4. Architecture — four layers

| Layer | Holds | Must never hold |
|---|---|---|
| `config/` | roles, credentials, menus, expected page text | logic |
| `pages/` | locators + navigation actions | assertions |
| `validations/` | named assertions built on `Verifier` | locators |
| `tests/` | flow + markers | selectors or credentials |
| `utils/` | highlighter, verifier, report, logger | application knowledge |

**Why split this way:** `pages/` knows *how* to reach and locate things,
`validations/` knows *what* must be true, `config/` holds *the expected values*.
Supplying a new expected heading later is a one-line edit in `config/menus.py` —
no test and no page object changes.

---

## 5. File map

```
D:\inride\
├── config/
│   ├── settings.py       env-driven config; the ONLY reader of os.environ
│   ├── roles.py          Role enum + credential resolution (password masked)
│   └── menus.py          expected menus + expected page text, per role  ← edit this most
├── pages/                locators + navigation. NO assertions.
│   ├── base_page.py      navigate, wait, screenshot
│   ├── login_page.py     login form + dynamic footer discovery
│   ├── app_shell.py      sidebar, top bar, 2FA reminder dismissal
│   └── conversations_page.py
├── validations/          named assertions. NO locators.
│   ├── login_validations.py
│   ├── navigation_validations.py
│   └── page_validations.py     fully config-driven
├── utils/
│   ├── highlight.py      yellow highlight engine (JS injection + style restore)
│   ├── verification.py   highlight-then-assert engine, soft assertions  ← the core
│   ├── report.py         assertion_report.html generator
│   └── logger.py
├── tests/
│   ├── conftest.py       role, page-object and browser-session fixtures
│   └── ui/
│       ├── test_login_page.py              2 tests
│       └── test_platform_admin_access.py   16 tests
├── conftest.py           browser wiring, verify fixture, failure hook, report hook
├── pytest.ini            markers, reporting
├── requirements.txt
├── run.ps1               PowerShell runner
├── DEMO-START.bat        double-click: headed smoke demo (~2 min)
├── DEMO-FULL.bat         double-click: headed full suite (~6 min)
├── RUN-HEADLESS.bat      double-click: full suite, no browser window
├── OPEN-REPORT.bat       double-click: open reports only
├── .env                  real credentials — GITIGNORED, never committed
├── .env.example          template with empty passwords
├── .github/workflows/playwright.yml
├── CLAUDE.md             rules for the assistant, auto-loaded each session
└── README.md
```

---

## 6. The three custom framework pieces

### `utils/highlight.py` — yellow highlighting

Requirement: before every UI assertion the target element must be visibly
highlighted so a human watching the headed browser sees what is being validated.

| Method | Does |
|---|---|
| `highlight()` | scrolls into view, paints yellow, holds for `HIGHLIGHT_MS` |
| `mark_failure()` | paints a **red** outline (kept, so the failure screenshot points at it) |
| `restore()` / `restore_all()` | puts the original inline style back |

The application is never permanently modified: the element's original inline
style is stashed on the element itself in a `data-qa-original-style` attribute
and restored afterwards. Verified: `0` elements retain the stash after a run.

Text colour is forced dark during highlight, because the app's light-on-dark
sidebar labels are unreadable on yellow.

### `utils/verification.py` — the `Verifier`

Every UI assertion goes through this. One call does six things:

```
1. scroll the element into view
2. paint it yellow
3. run the web-first Playwright assertion
4. record PASS/FAIL with expected + actual
5. on pass restore the style; on fail leave a red marker + screenshot
6. return instead of raising          ← soft assertion
```

Methods: `visible`, `has_text`, `contains_text`, `has_count`, `has_attribute`,
`url_is`, `custom`, `record_failure`, `record_info`.

**Why soft:** one missing element must not hide the state of the other 132
validations. Collected failures are raised in `pytest_runtest_call`
(**not** in the fixture teardown — that reports a test as an *error* while still
counting it as passed).

### `utils/report.py` — the assertion report

Generates `reports/assertion_report.html`: one row per validation with
description, expected, actual, PASS/FAIL badge, duration, timestamp and a link
to the failure screenshot. Grouped by test. This is the report shown to clients.

---

## 7. Roles and credentials

```text
PLATFORM_ADMIN    ← the only role executed in phase 1
DEALER_ADMIN      configured, not executed
USER              configured, not executed
READ_ONLY_USER    configured, not executed
```

Credentials resolve dynamically from `<ROLE>_USERNAME` / `<ROLE>_PASSWORD`
in `.env`. A test selects a role; it never sees a literal credential:

```python
credentials = credentials_for(Role.PLATFORM_ADMIN)
shell = LoginPage(page).open().login(credentials)
```

`Credentials.__repr__` renders the password as `'***'`, so it cannot leak into a
pytest failure line, a log record or an HTML report. **Do not bypass this.**

Adding a role later = one enum member + two `.env` keys. No code change.

---

## 8. Application quirks that break naive automation

### 8.1 The 2FA reminder dialog — critical

After every login the app shows a Radix `alertdialog`
(`data-testid="dialog-two-factor-reminder"`) with a full-screen
`bg-black/80` overlay that **intercepts every click**. No menu can be opened
until it is dismissed.

Dismiss with `button-two-factor-reminder-later` ("Maybe Later"). This is
read-only — it changes no account setting.

Handled in `AppShell.wait_until_ready()`. Never skip it.

### 8.2 Excellent `data-testid` coverage

This app is React/shadcn and exposes stable test ids everywhere. **Prefer
`get_by_test_id()` here**, ahead of role/text locators. Menu ids follow the
pattern `link-<kebab-case-name>`.

### 8.3 Slow staging under load

The QA environment occasionally takes far longer than 20s to hand over a route.
Menu clicks therefore use the navigation timeout (60s), not the element timeout.
This is a genuine environment characteristic, not a masked defect.

---

## 9. Discrepancies: requirement document vs. live application

Three strings in the original requirement do not match what the app renders.
The suite asserts the **actual UI text** and records the difference in the
report — neither silently passing nor falsely failing.

| Requirement asked for | Application renders | Page |
|---|---|---|
| `Manage Dealer Organization` | `Manage dealer organizations` | Dealer Profile |
| `Manage Users` / `Account & Permission` | `Manage user accounts and permissions` | Users |
| Conversations submenu `Text` | `SMS` | Conversations tabs |

Also note:
- **Automation Sequences** menu opens a page whose header reads **`Sequences`**
- **Push Notifications** opens **`Push Notification Preferences`**
- **Conversations** renders no `<h1>` — it is a tabbed workspace

**These need a decision from the client.** Once the intended wording is known,
it is a one-line change in `config/menus.py`.

---

## 10. Menu reference — all 14, verified

| # | Menu | test id | URL path | Page header |
|---|---|---|---|---|
| 1 | Conversations | `link-conversations` | `/` | *(tabs, no h1)* |
| 2 | Dealer Profile | `link-dealer-profile` | `/tenants` | Dealers |
| 3 | Users | `link-users` | `/users` | Users |
| 4 | Customer List | `link-customer-list` | `/leads` | Customer List |
| 5 | Campaigns | `link-campaigns` | `/cadences` | Campaigns |
| 6 | Campaign Steps | `link-campaign-steps` | `/cadence-steps` | Campaign Steps |
| 7 | Template Variants | `link-template-variants` | `/template-variants` | Template Variants |
| 8 | Email Templates | `link-email-templates` | `/email-templates` | Email Templates |
| 9 | Knowledge Base | `link-knowledge-base` | `/knowledge-base` | Knowledge Base |
| 10 | Reports | `link-reports` | `/reports` | Reports |
| 11 | Automation Sequences | `link-automation-sequences` | `/automation-sequences` | **Sequences** |
| 12 | Dealer SSO | `link-dealer-sso` | `/dealer-sso` | Dealer SSO |
| 13 | Push Notifications | `link-push-notifications` | `/notification` | **Push Notification Preferences** |
| 14 | Value Adjustments | `link-value-adjustments` | `/tenant-value-adjustments` | Value Adjustments |

Conversations submenus: `tab-email` ("Email"), `tab-sms` ("SMS").

Login page ids: `input-login-email`, `input-login-password`, `button-login`,
`button-signin-sso`, `button-google-signin`, `link-forgot-password`.
Logo alt text: `Trade Agent AI Logo`.
Footer link ids: `link-ai-terms`, `link-privacy`, `link-cookies`, `link-phone`,
`link-email`, `link-facebook`, `link-instagram`, `link-linkedin`, `link-twitter`.

---

## 11. Setting up in a fresh environment

```bash
git clone https://github.com/forhad2097/inride.git
cd inride

python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt      # Windows
# .venv/bin/python -m pip install -r requirements.txt            # Linux/macOS

.venv/Scripts/python.exe -m playwright install chromium

cp .env.example .env        # then fill in the four passwords
```

`.env` is gitignored on purpose — the passwords are **not** in the repository
and must be supplied separately.

---

## 12. Running

| Command | What it does | Time |
|---|---|---|
| `.\run.ps1 quick` or `DEMO-START.bat` | **headed** smoke demo, opens report | ~2 min |
| `.\run.ps1 demo` or `DEMO-FULL.bat` | **headed** full suite | ~6 min |
| `.\run.ps1` or `RUN-HEADLESS.bat` | full suite, no browser window | ~3 min |
| `.\run.ps1 login` | login page validations only | ~40 s |
| `.\run.ps1 menus` | menu / page access only | — |
| `.\run.ps1 report` / `OPEN-REPORT.bat` | open reports, run nothing | instant |

Raw pytest:
```bash
.venv/Scripts/python.exe -m pytest              # all
.venv/Scripts/python.exe -m pytest -m smoke     # by marker
.venv/Scripts/python.exe -m pytest --count 3    # flake check
```

Demo mode is three environment variables: `HEADLESS=false`, `SLOW_MO=250`,
`HIGHLIGHT_MS=700`.

**Browser windows per run: exactly two** — one guest session for the login page
tests, one authenticated session for the 16 access tests. If this number grows,
something has started depending on pytest-playwright's function-scoped `page`
fixture; see section 15.

---

## 13. Reports

All output lands in `D:\inride\reports\` (gitignored).

| File | Contents |
|---|---|
| `assertion_report.html` | **every individual validation** — expected, actual, pass/fail, evidence ← show this to clients |
| `report.html` | pytest-html: which test passed/failed, with logs |
| `screenshots/` | one screenshot per failed validation, offending element outlined red |
| `platform-admin-session-trace.zip` | full Playwright trace of the authenticated session |
| `login-page-session-trace.zip` | trace of the guest session |

Open a trace with:
```bash
.venv/Scripts/playwright.exe show-trace reports/platform-admin-session-trace.zip
```

---

## 14. Markers

```
smoke          fast critical-path checks
regression     full functional coverage
critical       P0 auth or access path
negative       invalid input and error handling
e2e            full multi-page journey
api            API-level, no browser
login          login page and authentication
menu           navigation and menu access
platform_admin / dealer_admin / user / read_only_user   role tags
```

`--strict-markers` is on: an unregistered marker is a collection error, not a
silent typo. Register new markers in `pytest.ini`.

---

## 15. Non-negotiable rules

1. Selectors live in `pages/`; expectations live in `config/menus.py`; tests hold neither.
2. **Every UI assertion goes through `verify.*`**, which highlights first. Never call `expect()` directly in a test.
3. Assertions are soft — they record and continue; the test fails once, in the call phase.
4. No `time.sleep()`, no `page.wait_for_timeout()` outside `utils/highlight.py`.
5. Locator priority here: `data-testid` → role → label → text → CSS.
6. Assertion descriptions read as a checklist: `"Platform Admin - Users menu is visible"`.
7. Passwords never appear in logs, reports or assertion messages.
8. `AppShell.wait_until_ready()` must run after login — the 2FA dialog blocks everything.
9. **Never make `page` an autouse dependency.** A fixture with `autouse=True`
   that depends on pytest-playwright's `page` opens a new browser context — a new
   visible window — for every test. This bug existed and was fixed; it produced 19
   windows instead of 2.
10. Never make a red test green by weakening the assertion.

---

## 16. Known history — bugs found and fixed in the framework itself

| Symptom | Cause | Fix |
|---|---|---|
| A new browser window opened before nearly every step in headed mode | `_timeouts` fixture had `autouse=True` and depended on `page`, forcing a fresh context per test | Removed autouse; two session-scoped windows (`guest_session`, `admin_session`) |
| Failing tests reported as `18 passed, 2 errors` | `verify.assert_all()` was raised in fixture teardown | Raised from a `pytest_runtest_call` wrapper instead → reports plain `FAILED` |
| Menu clicks timed out when staging was slow | Element timeout (20s) applied to route handover | Menu clicks use the navigation timeout (60s) |
| Sidebar labels unreadable when highlighted | White text on yellow background | Highlight forces a dark foreground, restored afterwards |

---

## 17. Where to make each kind of change

| You want to add | Edit |
|---|---|
| Another role's menu expectations | `MENUS_BY_ROLE` in `config/menus.py` |
| Exact expected text for a page | that menu's `page_texts` in `config/menus.py` |
| A new page's locators | a new class in `pages/` |
| A new named assertion | the matching class in `validations/` |
| Role-to-role menu comparison | parametrise the `role` fixture in `tests/conftest.py` |
| A new assertion type (e.g. `is_enabled`) | a method on `Verifier` in `utils/verification.py` |

None of that requires touching the highlighting, verification or reporting machinery.

---

## 18. Next phase — likely requests

The client has indicated these will come later:

- Dealer Admin / User / Read-Only User login and menu validation
- Comparing menu visibility between roles (permission matrix)
- Specific button and field validation per page
- CRUD permission validation
- API response validation
- Additional page-level assertions
- Negative test cases

The current structure supports all of these without a rewrite: roles are already
configured, `MENUS_BY_ROLE` is keyed by role, and the `role` fixture is a single
parametrisation point.

**Do not start any of this until explicitly instructed.**

---

## 19. Verification standard

Before reporting any work complete: run the tests, paste the real output, and
confirm `reports/assertion_report.html` shows 0 failures. Never claim green
without having seen it.

Last verified state: **18 tests, 133 validations, 0 failures, 2 browser windows,
~3 minutes headless.**
