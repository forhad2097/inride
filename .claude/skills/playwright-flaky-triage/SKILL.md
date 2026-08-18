---
name: playwright-flaky-triage
description: Use when a Playwright test fails, times out, passes locally but fails in CI, or passes and fails on re-run - a fixed diagnosis order for timeouts, strict-mode violations, race conditions and state leaks, plus how to read a trace. Use this instead of guessing at the fix or adding a retry.
---

# Playwright Failure & Flake Triage

**Never fix a failure you have not reproduced and explained.** Adding a retry, a sleep, or `--reruns` to make red go green is hiding a defect — possibly a real product bug the test correctly caught.

## Order of Diagnosis

### 1. Read the actual error, not the summary

Playwright errors are precise. Match the message to the cause:

| Error | Real cause | Fix |
|---|---|---|
| `Timeout 30000ms exceeded ... waiting for locator` | Element never matched | Wrong locator, or the app never rendered it. Check the trace's DOM snapshot. |
| `strict mode violation: resolved to N elements` | Locator is ambiguous | Scope it (`.filter()`, parent container) — do **not** reach for `.first()` |
| `Element is not stable` | Animation/layout shift mid-click | Assert on the settled state first, then act |
| `Element is outside of the viewport` | Lazy list / sticky overlay | `scroll_into_view_if_needed()` or dismiss the overlay |
| `Target page/context/browser has been closed` | Context torn down while an action was pending | Fixture scope mismatch — check `conftest.py` |
| `net::ERR_CONNECTION_REFUSED` | App under test is not running | Environment, not the test |

### 2. Reproduce it deliberately

```bash
.venv/Scripts/python.exe -m pytest tests/ui/test_x.py::test_y --count 10        # is it flaky or always red?
.venv/Scripts/python.exe -m pytest tests/ui/test_x.py::test_y --headed --slowmo 500   # watch it
.venv/Scripts/python.exe -m pytest tests/ui/test_x.py::test_y --tracing on      # capture evidence
playwright show-trace reports/traces/<name>.zip
```

Always red → real bug or wrong locator. Intermittent → race or state leak. Only red in parallel → state leak, go to step 4.

### 3. Read the trace before theorising

The trace timeline shows, per action: the DOM snapshot before/after, network calls, and console output. Look for:
- The element existing but with different text/attributes than expected
- A network request still pending when the assertion ran
- A console error at the moment of failure (the app broke, the test is right)

### 4. Classify the flake

| Class | Signature | Correct fix |
|---|---|---|
| **Race** | Assertion runs before the app updates | Use `expect()` (auto-retrying) instead of `assert`; wait on the *outcome*, not a delay |
| **State leak** | Passes alone, fails in a suite or with `-n 4` | Give each test its own data/user; kill shared module-scope fixtures holding mutable state |
| **Order dependency** | Fails when run in a different order | Test relies on a predecessor — make it self-sufficient |
| **Network timing** | Fails on slow CI only | Assert on the settled UI state, or `page.expect_response()` around the trigger |
| **Animation** | Intermittent wrong-element clicks | Wait for the container to be stable/visible before acting |
| **Time/locale** | Fails at date rollover or on a different machine | Freeze the clock / pin locale + timezone in the context |

### 5. Fix the cause, then prove it

Re-run `--count 10` after the fix. Green ten times = fixed. Green once = unknown.

## Hard bans

- `page.wait_for_timeout()` / `time.sleep()` as a fix
- `--reruns` to mask a known flake
- `.first()` to silence a strict-mode violation without checking *why* there are two matches
- Marking a test `skip` without a linked ticket and a date

## When the test is right and the app is wrong

Say so plainly, capture the trace + screenshot, and report it as a product defect. A test suite that gets weakened to match a broken app is worse than no suite.
