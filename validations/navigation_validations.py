"""Assertions about what a role can see and reach in the application shell."""

from __future__ import annotations

from config.menus import MenuItem, SubMenuItem
from config.roles import Role
from pages.app_shell import AppShell
from pages.conversations_page import ConversationsPage
from utils.verification import Verifier


class NavigationValidations:
    def __init__(self, verify: Verifier, shell: AppShell, role: Role) -> None:
        self.verify = verify
        self.shell = shell
        self.role = role
        self.prefix = role.display_name

    # --- authenticated state ----------------------------------------
    def validate_logged_in(self) -> None:
        self.verify.visible(
            self.shell.profile_menu, f"{self.prefix} - Login is successful (profile menu is visible)"
        )
        self.verify.visible(
            self.shell.sidebar_toggle,
            f"{self.prefix} - Application shell is accessible (sidebar is visible)",
        )
        self.verify.visible(
            self.shell.notifications_button,
            f"{self.prefix} - Notifications control is available after login",
        )

    # --- main menus --------------------------------------------------
    def validate_menu(self, item: MenuItem) -> None:
        """Highlight the sidebar entry, assert it is visible and correctly labelled."""
        link = self.shell.menu_link(item)
        self.verify.visible(link, f"{self.prefix} - {item.label} menu is visible")
        self.verify.has_text(
            link, item.label, f"{self.prefix} - {item.label} menu text is '{item.label}'"
        )

    def validate_all_menus(self, items: tuple[MenuItem, ...]) -> None:
        for item in items:
            self.validate_menu(item)

    def validate_menu_count(self, items: tuple[MenuItem, ...]) -> None:
        self.verify.record_info(
            f"{self.prefix} - Expected main menu count",
            f"{len(items)} menus configured for this role",
        )

    # --- submenus ----------------------------------------------------
    def validate_submenu(self, conversations: ConversationsPage, submenu: SubMenuItem) -> None:
        described_as = submenu.label
        if submenu.spec_name and submenu.spec_name != submenu.label:
            described_as = f"{submenu.label}' (requirement calls it '{submenu.spec_name})"
        tab = conversations.tab(submenu)
        self.verify.visible(
            tab, f"{self.prefix} - Conversations '{described_as}' submenu is visible"
        )
        self.verify.has_text(
            tab,
            submenu.label,
            f"{self.prefix} - Conversations submenu text is '{submenu.label}'",
        )
