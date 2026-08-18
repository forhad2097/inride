"""Reusable highlight-then-assert engine with soft assertions and reporting.

Every UI check goes through :class:`Verifier`. One call:

1. scrolls the element into view,
2. paints it yellow so a human watching the browser sees what is being checked,
3. runs a web-first Playwright assertion,
4. records a named PASS/FAIL result with expected vs. actual,
5. restores the element (or leaves a red marker + screenshot on failure),
6. **returns instead of raising**, so one missing element does not abort the
   remaining independent validations.

The test fails at teardown, via :meth:`Verifier.assert_all`, listing every
failure at once.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable

from playwright.sync_api import Locator, Page, expect

from config.settings import SCREENSHOT_DIR, settings
from utils.highlight import Highlighter
from utils.logger import get_logger

log = get_logger("verify")


class Status(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"


@dataclass
class VerificationResult:
    description: str
    status: Status
    expected: str = ""
    actual: str = ""
    test_name: str = ""
    location: str = ""
    duration_ms: int = 0
    screenshot: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))

    @property
    def passed(self) -> bool:
        return self.status is Status.PASSED


#: every result produced during the session, used to build the HTML report
SESSION_RESULTS: list[VerificationResult] = []


def _safe_filename(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text)[:110].strip("_")


class Verifier:
    """Collects verification results for one test."""

    def __init__(self, test_name: str, highlighter: Highlighter | None = None) -> None:
        self.test_name = test_name
        self.highlighter = highlighter or Highlighter()
        self.results: list[VerificationResult] = []

    # --- assertions -------------------------------------------------
    def visible(self, locator: Locator, description: str, *, timeout: int | None = None) -> bool:
        return self._check(
            locator,
            description,
            lambda: expect(locator.first).to_be_visible(timeout=timeout or settings.default_timeout),
            expected="element is visible",
            actual_fn=lambda: self._state_of(locator),
        )

    def has_text(
        self, locator: Locator, expected_text: str, description: str, *, timeout: int | None = None
    ) -> bool:
        return self._check(
            locator,
            description,
            lambda: expect(locator.first).to_have_text(
                expected_text, timeout=timeout or settings.default_timeout
            ),
            expected=f"text == {expected_text!r}",
            actual_fn=lambda: repr(self._text_of(locator)),
        )

    def contains_text(
        self, locator: Locator, expected_text: str, description: str, *, timeout: int | None = None
    ) -> bool:
        return self._check(
            locator,
            description,
            lambda: expect(locator.first).to_contain_text(
                expected_text, timeout=timeout or settings.default_timeout
            ),
            expected=f"text contains {expected_text!r}",
            actual_fn=lambda: repr(self._text_of(locator)),
        )

    def has_count(self, locator: Locator, count: int, description: str) -> bool:
        return self._check(
            locator,
            description,
            lambda: expect(locator).to_have_count(count, timeout=settings.default_timeout),
            expected=f"count == {count}",
            actual_fn=lambda: str(self._count_of(locator)),
        )

    def has_attribute(
        self, locator: Locator, name: str, value: str | re.Pattern, description: str
    ) -> bool:
        return self._check(
            locator,
            description,
            lambda: expect(locator.first).to_have_attribute(
                name, value, timeout=settings.default_timeout
            ),
            expected=f"@{name} == {value!r}",
            actual_fn=lambda: repr(self._attr_of(locator, name)),
        )

    def url_is(self, page: Page, expected_url: str | re.Pattern, description: str) -> bool:
        """Page-level assertion - nothing to highlight, but still recorded."""
        started = time.perf_counter()
        try:
            expect(page).to_have_url(expected_url, timeout=settings.navigation_timeout)
        except AssertionError as exc:
            return self._record(
                description,
                Status.FAILED,
                expected=f"url == {expected_url!r}",
                actual=page.url,
                started=started,
                detail=str(exc),
                screenshot=self._screenshot(page, description),
            )
        return self._record(
            description, Status.PASSED, expected=f"url == {expected_url!r}",
            actual=page.url, started=started,
        )

    def custom(
        self, description: str, assertion: Callable[[], None], *, expected: str = "", actual: str = ""
    ) -> bool:
        """Escape hatch for a check that is not element-shaped."""
        started = time.perf_counter()
        try:
            assertion()
        except AssertionError as exc:
            return self._record(
                description, Status.FAILED, expected=expected, actual=actual or str(exc)[:300],
                started=started, detail=str(exc),
            )
        return self._record(description, Status.PASSED, expected=expected, actual=actual, started=started)

    def record_failure(self, description: str, reason: str, page: Page | None = None) -> bool:
        """Log a failure that is not an assertion - e.g. a menu that could not
        be opened - so the flow can continue and the report stays complete."""
        return self._record(
            description,
            Status.FAILED,
            expected="step completes",
            actual=reason[:400],
            started=time.perf_counter(),
            detail=reason,
            screenshot=self._screenshot(page, description) if page else "",
        )

    def record_info(self, description: str, actual: str) -> bool:
        """Record an observed value that is captured but not yet asserted
        (used while exact expected text is still to be supplied)."""
        return self._record(
            description, Status.PASSED, expected="captured for reporting",
            actual=actual, started=time.perf_counter(),
        )

    # --- lifecycle --------------------------------------------------
    @property
    def failures(self) -> list[VerificationResult]:
        return [r for r in self.results if not r.passed]

    def assert_all(self) -> None:
        """Fail the test if anything failed - called once, at teardown."""
        if not self.failures:
            return
        lines = [
            f"{len(self.failures)} of {len(self.results)} verifications failed "
            f"in {self.test_name}:",
            "",
        ]
        for i, result in enumerate(self.failures, 1):
            lines.append(f"  {i}. {result.description}")
            lines.append(f"       expected : {result.expected}")
            lines.append(f"       actual   : {result.actual}")
            if result.screenshot:
                lines.append(f"       screenshot: {result.screenshot}")
        raise AssertionError("\n".join(lines))

    # --- internals --------------------------------------------------
    def _check(
        self,
        locator: Locator,
        description: str,
        assertion: Callable[[], None],
        *,
        expected: str,
        actual_fn: Callable[[], str],
    ) -> bool:
        started = time.perf_counter()
        self.highlighter.highlight(locator)
        try:
            assertion()
        except AssertionError as exc:
            self.highlighter.mark_failure(locator)
            return self._record(
                description,
                Status.FAILED,
                expected=expected,
                actual=self._safe(actual_fn),
                started=started,
                detail=str(exc),
                screenshot=self._screenshot(self._page_of(locator), description),
            )
        except Exception as exc:  # noqa: BLE001 - locator/timeout problems
            self.highlighter.mark_failure(locator)
            return self._record(
                description,
                Status.FAILED,
                expected=expected,
                actual=f"{type(exc).__name__}: {str(exc)[:250]}",
                started=started,
                detail=str(exc),
                screenshot=self._screenshot(self._page_of(locator), description),
            )
        else:
            self.highlighter.restore(locator)
            return self._record(
                description, Status.PASSED, expected=expected,
                actual=self._safe(actual_fn), started=started,
            )

    def _record(
        self,
        description: str,
        status: Status,
        *,
        expected: str,
        actual: str,
        started: float,
        detail: str = "",
        screenshot: str = "",
    ) -> bool:
        result = VerificationResult(
            description=description,
            status=status,
            expected=expected,
            actual=actual,
            test_name=self.test_name,
            duration_ms=int((time.perf_counter() - started) * 1000),
            screenshot=screenshot,
        )
        self.results.append(result)
        SESSION_RESULTS.append(result)
        if result.passed:
            log.info("PASS | %s | actual=%s", description, actual)
        else:
            log.error("FAIL | %s | expected=%s | actual=%s", description, expected, actual)
            if detail:
                log.error("       %s", detail.splitlines()[0][:200])
        return result.passed

    # --- best-effort readers (never raise) --------------------------
    @staticmethod
    def _safe(fn: Callable[[], str]) -> str:
        try:
            return fn()
        except Exception:  # noqa: BLE001
            return "<unreadable>"

    @staticmethod
    def _page_of(locator: Locator) -> Page | None:
        try:
            return locator.page
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _state_of(locator: Locator) -> str:
        count = locator.count()
        if count == 0:
            return "not found in the DOM"
        return f"found {count} match(es), visible={locator.first.is_visible()}"

    @staticmethod
    def _text_of(locator: Locator) -> str:
        if locator.count() == 0:
            return "<element not found>"
        return (locator.first.inner_text() or "").strip()

    @staticmethod
    def _count_of(locator: Locator) -> int:
        return locator.count()

    @staticmethod
    def _attr_of(locator: Locator, name: str) -> str:
        if locator.count() == 0:
            return "<element not found>"
        return locator.first.get_attribute(name) or ""

    def _screenshot(self, page: Page | None, description: str) -> str:
        if page is None:
            return ""
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        path = SCREENSHOT_DIR / f"FAIL_{_safe_filename(description)}.png"
        try:
            page.screenshot(path=str(path))
        except Exception as exc:  # noqa: BLE001
            log.debug("could not capture screenshot: %s", exc)
            return ""
        return str(path.relative_to(SCREENSHOT_DIR.parent))
