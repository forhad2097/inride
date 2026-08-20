# inride — Trade Agent AI Test Automation

Playwright (Python) + pytest UI automation for **Trade Agent AI**
(`https://agentai-qa.inride.com`), structured with the Page Object Model.

**Phase 1 scope:** Login page validation + Platform Admin login + Platform Admin
menu/page access validation. Read-only — nothing is created, edited or deleted.

---

## Quick start

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
Copy-Item .env.example .env      # then fill in the passwords

.\run.ps1                 # full suite, headless
.\run.ps1 demo            # HEADED + slow motion + long highlight  <- for a client demo
.\run.ps1 login           # login page validations only
.\run.ps1 menus           # menu / page access validations only
.\run.ps1 report          # open the reports
```

Reports land in:

| File | What it answers |
|---|---|
| `reports/assertion_report.html` | **every individual validation** — expected, actual, pass/fail, evidence |
| `reports/report.html` | pytest-html: which test passed/failed, with logs |
| `reports/screenshots/` | one screenshot per failed validation |
| `reports/platform-admin-session-trace.zip` | full Playwright trace of the authenticated session |

---

## Yellow highlighting

Before **every** UI assertion the target element is scrolled into view and
painted yellow, so a human watching the headed browser sees exactly what is
being validated at that moment.

```python
verify.visible(shell.menu_link(USERS), "Platform Admin - Users menu is visible")
```

That single call: scrolls → highlights yellow → holds for `HIGHLIGHT_MS` →
asserts → restores the original style → records the result.

- Implemented once in [utils/highlight.py](utils/highlight.py); never duplicated in a test.
- The application is **never permanently modified** — the element's original
  inline style is stashed on the element and restored afterwards, and
  `restore_all()` is a teardown safety net.
- A **failed** assertion deliberately keeps a **red** marker so the failure
  screenshot points straight at the offending element.
- Tunable from `.env`: `HIGHLIGHT_ENABLED`, `HIGHLIGHT_MS`, `HIGHLIGHT_BACKGROUND`,
  `HIGHLIGHT_OUTLINE`, `HIGHLIGHT_FOREGROUND`.

---

## Project structure

```
inride/
├── config/
│   ├── settings.py        # env-driven config; the only reader of os.environ
│   ├── roles.py           # Role enum + credential resolution (password masked)
│   ├── menus.py           # expected menus + expected page text, per role
│   ├── login_page.py      # expected login page copy: form, footer, copyright
│   └── two_factor.py      # expected copy of the three post-login 2FA dialogs
├── pages/                 # locators + navigation. NO assertions.
│   ├── base_page.py
│   ├── login_page.py      # locators grouped: form, password toggle, footer
│   ├── app_shell.py       # sidebar, top bar, 2FA reminder handling
│   ├── two_factor.py      # the post-login 2FA dialog chain
│   └── conversations_page.py
├── validations/           # named assertions. NO locators.
│   ├── login_validations.py
│   ├── two_factor_validations.py
│   ├── navigation_validations.py
│   └── page_validations.py
├── utils/
│   ├── highlight.py       # the reusable yellow-highlight helper
│   ├── verification.py    # highlight-then-assert engine, soft assertions
│   ├── report.py          # assertion_report.html generator
│   └── logger.py
├── tests/
│   ├── conftest.py        # role, page-object and authenticated-session fixtures
│   └── ui/
│       ├── test_login_page.py
│       └── test_platform_admin_access.py
├── conftest.py            # browser wiring, verify fixture, report hook
├── pytest.ini             # markers, reporting
└── run.ps1
```

**Why the layers are split:** `pages/` knows *how* to reach and locate things;
`validations/` knows *what* must be true; `config/` holds *the expected values*.
Adding a new expected heading later is a one-line edit in `config/menus.py` —
no test and no page object changes.

---

## Roles

```text
PLATFORM_ADMIN    <- the only role executed in this phase
DEALER_ADMIN      configured, not executed
USER              configured, not executed
READ_ONLY_USER    configured, not executed
```

Credentials are resolved dynamically from `<ROLE>_USERNAME` / `<ROLE>_PASSWORD`
in `.env`. A test selects a role; it never sees a literal credential:

```python
credentials = credentials_for(Role.PLATFORM_ADMIN)
shell = LoginPage(page).open().login(credentials)
```

`Credentials.__repr__` renders the password as `'***'`, so it cannot leak into a
pytest failure line, a log record or an HTML report.

---

## Coverage — 20 tests, 240 validations

| Suite | Tests | Validations |
|---|---|---|
| Login page — branding, title, labels, form controls | 1 | 22 |
| Login page — full footer (logo, Legal, Contact Info, social, copyright) | 1 | 50 |
| Login page — password show/hide, then valid login | 1 | 15 |
| Post-login 2FA dialog chain (reminder → settings → setup → cancel → close) | 1 | 54 |
| Platform Admin login | 1 | 3 |
| All 14 main menus | 1 | 29 |
| Conversations → Email / SMS submenus | 1 | 5 |
| Dealer Profile page | 1 | 7 |
| Users page | 1 | 7 |
| Remaining 11 menus (one test each) | 11 | 48 |

Every remaining menu is a **separate parametrised test**, so a failure names the
menu that broke instead of failing one giant test.

---

## Findings — application text vs. the requirement document

Four requirement strings do not match what the application renders. The suite
asserts the **actual UI text** and records the difference in the report rather
than silently passing or failing:

| Requirement asked for | Application renders | Where |
|---|---|---|
| `Copyright 2026, Inright LLC, All Rights Reserved` | `© Copyright 2026 Inride LLC. All Rights Reserved.` | Login footer |
| `Manage Dealer Organization` | `Manage dealer organizations` | Dealer Profile |
| `Manage Users` / `Account & Permission` | `Manage user accounts and permissions` | Users |
| Conversations submenu `Text` | `SMS` | Conversations tabs |

The copyright line differs in four ways: a leading `©`, spaces instead of the
commas, a trailing full stop, and the company spelled **`Inride`** rather than
`Inright` — which matches the `inride.com` domain, so the requirement's spelling
looks like a typo. Confirm which is correct and it is a one-line change.

Also worth noting: the **Automation Sequences** menu opens a page whose header
reads **`Sequences`**, and **Push Notifications** opens **`Push Notification
Preferences`**.

Supply the intended wording and it is a one-line change in `config/menus.py`
(pages) or `config/login_page.py` (login page and footer).

---

## Error handling

- Assertions are **soft**: a missing element records a failure and the run
  continues, so one broken menu never hides the state of the other thirteen.
- Each failure captures expected vs. actual, a screenshot, and a red marker on
  the element.
- The test fails once, at teardown, listing every failure together.
- A menu that cannot even be opened is recorded as a failure and that menu's
  remaining checks are skipped — the other menus are separate tests and still run.

---

## Adding the next phase

| You want to add | Edit |
|---|---|
| Another role's menu expectations | `MENUS_BY_ROLE` in `config/menus.py` |
| Exact expected text for a page | that menu's `page_texts` in `config/menus.py` |
| A new page's locators | a new class in `pages/` |
| A new named assertion | the matching class in `validations/` |
| Role-to-role menu comparison | parametrise the `role` fixture in `tests/conftest.py` |

No part of that requires touching the highlighting, verification or reporting
machinery.

---

## Post-login two-factor flow

The account under test has two-factor authentication switched off, so the
application raises a reminder popup after every login. The suite walks the whole
chain and backs out of it:

```
successful login
  └─ Reminder popup        "Protect your account with 2FA"
       ├─ assert title, description, "Maybe Later", "Open Security Settings"
       └─ click Open Security Settings          (not Maybe Later)
            └─ Settings popup   "Two-Factor Authentication"
                 ├─ assert subtitle, "2FA is Disabled", description, Enable button, Close (X)
                 └─ click Enable 2FA
                      └─ Setup popup   "Setup Two-Factor Authentication"
                           ├─ assert QR instruction and QR image (presence only)
                           ├─ assert manual code label and code   (presence only)
                           ├─ assert 6-digit label and input      (never filled)
                           ├─ assert Cancel and "Verify & Enable" (never clicked)
                           └─ click Cancel
                                └─ back on the Settings popup, still "2FA is Disabled"
                                     └─ click Close (X) → authenticated app
```

**Nothing is switched on.** `Enable 2FA` only requests a setup secret and renders
the QR screen; two-factor authentication is activated by `Verify & Enable`, which
is asserted but never clicked. Verified after every run: the account still logs
in with no authenticator prompt and still reports `2FA is Disabled`.

Dynamic values — the QR image and the 32-character manual setup code — are
asserted for **presence only**. The manual code is additionally treated as a
secret: only its length reaches the report, never its value.

Popups 2 and 3 are the **same** dialog element (`dialog-2fa-settings`)
re-rendered, so they are told apart by their heading, never by the container.
