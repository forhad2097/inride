---
name: qa-test-design
description: Use when turning a requirement, user story, bug report or client demo brief into concrete automated test cases - applies equivalence partitioning, boundary values, negative and edge coverage, risk-based prioritisation, and the naming/tagging convention used in this repo. Read this BEFORE writing test files, so you automate the right cases instead of only the happy path.
---

# QA Test Case Design

Automating the happy path only is the most common way a suite gives false confidence. This is the process for deciding *what* to automate before deciding *how*.

## Step 1 — Restate the requirement as observable behaviour

Write it as: **Given** \<state\> **When** \<action\> **Then** \<observable result\>.

If you cannot name what a user or an API response would visibly show, you cannot assert it. Go get clarification instead of guessing.

## Step 2 — Derive cases with the four lenses

| Lens | Question | Example (login) |
|---|---|---|
| **Positive** | Does it work for the intended user? | valid user → inventory page |
| **Negative** | What does it do when the input is wrong? | wrong password → error banner |
| **Boundary** | What happens at the edges of the allowed range? | 0-char, 1-char, max-length, max+1 |
| **State / flow** | What happens out of order, twice, or after a break? | locked-out user, back-button after logout, double submit |

Equivalence partitioning: pick **one** representative per class, not ten. Three valid emails test the same code path once.

## Step 3 — Prioritise by risk, not by ease

Risk = likelihood of failure × business cost of failure.

| Priority | Marker | Meaning |
|---|---|---|
| P0 | `@pytest.mark.critical` + `smoke` | Revenue/auth path. Broken = product unusable. Must run on every commit. |
| P1 | `regression` | Core feature, high usage. Runs on every PR. |
| P2 | `regression` | Secondary flows, cosmetic, rare states. Nightly. |

Automate P0 first, completely, before touching P2. A demo shows P0 depth, not P2 breadth.

## Step 4 — Name the test for the behaviour

```
test_<subject>_<condition>_<expected outcome>
```
Good: `test_locked_out_user_sees_lockout_error`
Bad: `test_login_2`, `test_login_flow`, `test_it_works`

A reader who never sees the body must know what broke when it goes red.

## Step 5 — Keep tests independent

Each test creates its own state and asserts one behaviour. No test may depend on another test having run first — parallel execution (`-n 4`) reorders everything. If two tests need the same setup, that is a fixture, not an ordering dependency.

## Step 6 — Write the traceability line

Every test file starts with a docstring mapping tests to the requirement/ticket they cover. This is what you show a client when they ask "what does the suite actually prove?"

## Anti-patterns to reject in review

| Smell | Why it is wrong |
|---|---|
| One test with 12 assertions across 4 pages | First failure hides the rest; the name cannot describe it |
| `test_end_to_end_everything` | Untriageable when red |
| Tests that pass whether or not the feature works | Assert on the observable outcome, not on the click succeeding |
| Sleeping to "let the page settle" | Hides a real race condition; see `playwright-python-pom` |
| Hardcoded prod credentials in the test file | Config + `.env`, always |

## Output of this skill

A short table — case name, priority, marker, precondition, expected result — agreed *before* code is written. Then implement with `playwright-python-pom`.
