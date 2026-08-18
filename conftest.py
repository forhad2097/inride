"""Root fixtures: browser wiring, verification, reporting.

pytest-playwright supplies ``browser`` / ``page``; only what the project needs
is overridden here.
"""

from __future__ import annotations

import pytest

from config.settings import REPORTS_DIR, SCREENSHOT_DIR, settings
from utils.highlight import Highlighter
from utils.logger import get_logger
from utils.report import write_assertion_report
from utils.verification import SESSION_RESULTS, Verifier

log = get_logger("conftest")

#: where each test's Verifier is parked so the call-phase hook can find it
VERIFIER_KEY = pytest.StashKey[Verifier]()


# ---------------------------------------------------------------- setup
@pytest.fixture(scope="session", autouse=True)
def _prepare_directories() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def base_url() -> str:
    return settings.url


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    return {
        **browser_type_launch_args,
        "headless": settings.headless,
        "slow_mo": settings.slow_mo,
    }


@pytest.fixture(scope="session")
def context_options() -> dict:
    """Shared context options, used by pytest-playwright's context and by the
    long-lived authenticated context in tests/conftest.py."""
    return {
        "viewport": {"width": 1440, "height": 900},
        "locale": "en-US",
        "timezone_id": "UTC",
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, context_options: dict) -> dict:
    return {**browser_context_args, **context_options}


def new_session(browser, options: dict, trace_name: str):
    """Open ONE browser context + page and keep it for a whole suite.

    Deliberately not pytest-playwright's function-scoped ``page``: that fixture
    opens a fresh context - i.e. a fresh browser window in headed mode - for
    every single test. Two long-lived sessions (guest + authenticated) keep the
    demo to two windows and make the run watchable.
    """
    context = browser.new_context(**options)
    context.set_default_timeout(settings.default_timeout)
    context.set_default_navigation_timeout(settings.navigation_timeout)
    context.tracing.start(screenshots=True, snapshots=True, sources=False)

    page = context.new_page()
    try:
        yield page
    finally:
        try:
            context.tracing.stop(path=str(REPORTS_DIR / f"{trace_name}-trace.zip"))
        finally:
            context.close()


# ------------------------------------------------- highlight + verify
@pytest.fixture(scope="session")
def highlighter() -> Highlighter:
    return Highlighter()


@pytest.fixture
def verify(request, highlighter: Highlighter):
    """Soft-assertion recorder: a failed check is recorded and the test carries
    on, so one missing element never hides the rest of the run.

    The collected failures are raised by ``pytest_runtest_call`` below - not
    here. Raising from a fixture's teardown would report the test as an *error*
    while still counting it as passed; raising during the call phase reports it
    as a plain FAILED, which is what a report must show.
    """
    verifier = Verifier(test_name=request.node.name, highlighter=highlighter)
    request.node.stash[VERIFIER_KEY] = verifier
    yield verifier
    passed = len(verifier.results) - len(verifier.failures)
    log.info(
        "%s: %s/%s verifications passed", request.node.name, passed, len(verifier.results)
    )


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    """Turn recorded soft-assertion failures into a normal test failure."""
    result = yield
    verifier = item.stash.get(VERIFIER_KEY, None)
    if verifier is not None:
        verifier.assert_all()
    return result


# ------------------------------------------------------------ reporting
def pytest_sessionfinish(session, exitstatus) -> None:  # noqa: ARG001
    if not SESSION_RESULTS:
        return
    path = write_assertion_report()
    failed = sum(1 for r in SESSION_RESULTS if not r.passed)
    print(
        f"\n---- Assertion report: {len(SESSION_RESULTS)} validations, "
        f"{len(SESSION_RESULTS) - failed} passed, {failed} failed"
        f"\n---- {path}"
    )


def pytest_html_report_title(report) -> None:
    report.title = "inride - Playwright Automation Report"
