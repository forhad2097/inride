"""Destination-page assertions.

Driven entirely by ``config/menus.py``: give a :class:`MenuItem` a ``heading``
or another ``ExpectedText`` and it is asserted here without any new code.
"""

from __future__ import annotations

from config.menus import MenuItem
from config.roles import Role
from pages.app_shell import AppShell
from utils.verification import Verifier


class PageValidations:
    def __init__(self, verify: Verifier, shell: AppShell, role: Role) -> None:
        self.verify = verify
        self.shell = shell
        self.role = role
        self.prefix = role.display_name

    def validate_page_loaded(self, item: MenuItem) -> None:
        """The application navigated to the page this menu owns."""
        self.verify.custom(
            f"{self.prefix} - {item.label} page loaded (URL is '{item.path}')",
            lambda: _assert_path(self.shell.path, item.path),
            expected=f"path == {item.path!r}",
            actual=self.shell.path,
        )

    def validate_primary_header(self, item: MenuItem) -> None:
        """Highlight and assert the page's primary header."""
        if item.heading is None:
            self.verify.record_info(
                f"{self.prefix} - {item.label} page renders no primary header",
                "page uses a tabbed workspace instead of an <h1>",
            )
            return

        heading = self.shell.heading(item.heading)
        self.verify.visible(
            heading, f"{self.prefix} - {item.label} page header is visible"
        )
        self.verify.has_text(
            heading,
            item.heading,
            f"{self.prefix} - {item.label} page header text is '{item.heading}'",
        )
        self.verify.record_info(
            f"{self.prefix} - {item.label} page header captured",
            item.heading,
        )

    def validate_expected_texts(self, item: MenuItem) -> None:
        for expected in item.page_texts:
            locator = self.shell.text(expected.value, exact=not expected.partial)
            description = f"{self.prefix} - {item.label} {expected.label} is visible"
            self.verify.visible(locator, description)
            self.verify.contains_text(
                locator,
                expected.value,
                f"{self.prefix} - {item.label} {expected.label} text is '{expected.value}'",
            )
            if expected.spec_text and expected.spec_text != expected.value:
                self.verify.record_info(
                    f"{self.prefix} - {item.label} {expected.label}: wording differs from the "
                    f"requirement document",
                    f"requirement asked for '{expected.spec_text}', "
                    f"application renders '{expected.value}'",
                )

    def validate(self, item: MenuItem) -> None:
        """Full page check: URL, primary header, configured texts."""
        self.validate_page_loaded(item)
        self.validate_primary_header(item)
        self.validate_expected_texts(item)


def _assert_path(actual: str, expected: str) -> None:
    assert actual.rstrip("/") == expected.rstrip("/") or actual == expected, (
        f"expected path {expected!r}, landed on {actual!r}"
    )
