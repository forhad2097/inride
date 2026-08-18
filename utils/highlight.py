"""Temporary yellow highlighting of the element currently under assertion.

Purpose: when the suite runs headed, a human watching the browser can see
exactly which element the automation is validating at that moment.

The application is never permanently modified - the element's original inline
style is stashed on the element itself before the highlight is applied and
restored afterwards. The one deliberate exception is a failed assertion: the
element keeps a red marker so the failure screenshot shows what went wrong.
"""

from __future__ import annotations

from playwright.sync_api import Locator

from config.settings import settings
from utils.logger import get_logger

log = get_logger(__name__)

_STASH_ATTR = "data-qa-original-style"

_APPLY_JS = """
(el, opts) => {
    if (!el.hasAttribute(opts.attr)) {
        el.setAttribute(opts.attr, JSON.stringify({
            outline: el.style.outline,
            outlineOffset: el.style.outlineOffset,
            backgroundColor: el.style.backgroundColor,
            boxShadow: el.style.boxShadow,
            transition: el.style.transition,
            color: el.style.color,
        }));
    }
    el.style.transition = 'none';
    el.style.outline = opts.outline;
    el.style.outlineColor = opts.outlineColor;
    el.style.outlineOffset = '2px';
    if (opts.background) {
        el.style.backgroundColor = opts.background;
        // keep the label readable: light-on-yellow is unreadable on a dark theme
        el.style.color = opts.foreground;
        el.querySelectorAll('*').forEach(child => {
            child.setAttribute(opts.childAttr, child.style.color || '');
            child.style.color = opts.foreground;
        });
    }
    el.style.boxShadow = opts.shadow;
    return true;
}
"""

_RESTORE_JS = """
(el, attr) => {
    const raw = el.getAttribute(attr);
    if (raw === null) { return false; }
    const prev = JSON.parse(raw);
    el.style.outline = prev.outline || '';
    el.style.outlineOffset = prev.outlineOffset || '';
    el.style.backgroundColor = prev.backgroundColor || '';
    el.style.boxShadow = prev.boxShadow || '';
    el.style.transition = prev.transition || '';
    el.style.color = prev.color || '';
    el.querySelectorAll('[' + attr + '-child]').forEach(child => {
        child.style.color = child.getAttribute(attr + '-child') || '';
        child.removeAttribute(attr + '-child');
    });
    el.removeAttribute(attr);
    return true;
}
"""


_RESTORE_ALL_JS = """
(attr) => {
    document.querySelectorAll('[' + attr + ']').forEach(el => {
        const prev = JSON.parse(el.getAttribute(attr));
        el.style.outline = prev.outline || '';
        el.style.outlineOffset = prev.outlineOffset || '';
        el.style.backgroundColor = prev.backgroundColor || '';
        el.style.boxShadow = prev.boxShadow || '';
        el.style.transition = prev.transition || '';
        el.style.color = prev.color || '';
        el.removeAttribute(attr);
    });
    document.querySelectorAll('[' + attr + '-child]').forEach(child => {
        child.style.color = child.getAttribute(attr + '-child') || '';
        child.removeAttribute(attr + '-child');
    });
}
"""


class Highlighter:
    """Applies and removes the temporary visual marker.

    Every method is best-effort: highlighting is a diagnostic aid, so a failure
    to highlight must never turn a passing assertion into a failing one.
    """

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        duration_ms: int | None = None,
    ) -> None:
        self.enabled = settings.highlight_enabled if enabled is None else enabled
        self.duration_ms = settings.highlight_ms if duration_ms is None else duration_ms

    # --- public API -------------------------------------------------
    def highlight(self, locator: Locator, *, pause: bool = True) -> None:
        """Scroll the element into view and paint it yellow."""
        if not self.enabled:
            return
        self._apply(
            locator,
            outline=settings.highlight_outline,
            outline_color=settings.highlight_outline_color,
            background=settings.highlight_background,
            shadow="0 0 0 6px rgba(255, 193, 7, 0.35)",
            scroll=True,
        )
        if pause and self.duration_ms > 0:
            self._pause(locator, self.duration_ms)

    def mark_failure(self, locator: Locator) -> None:
        """Leave a red marker on an element whose assertion failed, so the
        failure screenshot points at it. Intentionally not restored."""
        if not self.enabled:
            return
        self._apply(
            locator,
            outline=settings.failure_outline,
            outline_color=settings.failure_outline_color,
            background=None,
            shadow="0 0 0 6px rgba(229, 57, 53, 0.35)",
            scroll=False,
        )

    def restore(self, locator: Locator) -> None:
        """Put the element's original inline style back."""
        if not self.enabled:
            return
        try:
            locator.first.evaluate(_RESTORE_JS, _STASH_ATTR, timeout=2000)
        except Exception as exc:  # noqa: BLE001 - diagnostics must not fail a test
            log.debug("could not restore highlight: %s", exc)

    def restore_all(self, page) -> None:
        """Safety net: clear any marker left behind on the page."""
        if not self.enabled:
            return
        try:
            page.evaluate(_RESTORE_ALL_JS, _STASH_ATTR)
        except Exception as exc:  # noqa: BLE001
            log.debug("could not clear highlights: %s", exc)

    # --- internals --------------------------------------------------
    def _apply(
        self,
        locator: Locator,
        *,
        outline: str,
        outline_color: str,
        background: str | None,
        shadow: str,
        scroll: bool,
    ) -> None:
        target = locator.first
        try:
            if scroll:
                target.scroll_into_view_if_needed(timeout=5000)
            target.evaluate(
                _APPLY_JS,
                {
                    "attr": _STASH_ATTR,
                    "childAttr": f"{_STASH_ATTR}-child",
                    "outline": outline,
                    "outlineColor": outline_color,
                    "background": background,
                    "foreground": settings.highlight_foreground,
                    "shadow": shadow,
                },
                timeout=5000,
            )
        except Exception as exc:  # noqa: BLE001
            # Element missing / detached - the assertion that follows will
            # report the real problem with a far better message than this.
            log.debug("could not highlight element: %s", exc)

    @staticmethod
    def _pause(locator: Locator, ms: int) -> None:
        try:
            locator.page.wait_for_timeout(ms)
        except Exception as exc:  # noqa: BLE001
            log.debug("highlight pause skipped: %s", exc)
