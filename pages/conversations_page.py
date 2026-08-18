"""Conversations workspace - the Email / SMS tabs.

Read-only: nothing here sends a message or mutates a thread.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.menus import SubMenuItem
from pages.base_page import BasePage


class ConversationsPage(BasePage):
    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.tab_list: Locator = page.get_by_role("tablist")
        self.thread_search: Locator = page.get_by_test_id("thread-search-bar-input")
        self.filters_button: Locator = page.get_by_test_id("button-open-filters")

    def tab(self, submenu: SubMenuItem) -> Locator:
        return self.page.get_by_test_id(submenu.test_id)
