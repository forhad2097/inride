"""Login page validation - runs before any credential is entered.

| Case                                    | Priority | Covers                    |
|-----------------------------------------|----------|---------------------------|
| branding and login form are displayed   | P0       | LOGIN-01 .. LOGIN-10      |
| footer items are detected and displayed | P1       | LOGIN-11 (dynamic footer) |
"""

import pytest

from config.roles import Role
from pages.login_page import LoginPage
from utils.verification import Verifier
from validations.login_validations import LoginPageValidations


@pytest.fixture
def login_validations(verify: Verifier, login_page: LoginPage, role: Role):
    login_page.open()
    return LoginPageValidations(verify, login_page, role)


@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.login
def test_login_page_shows_branding_and_login_form(login_validations: LoginPageValidations):
    login_validations.validate_branding()
    login_validations.validate_login_form()


@pytest.mark.smoke
@pytest.mark.login
def test_login_page_footer_items_are_displayed(login_validations: LoginPageValidations):
    login_validations.validate_footer()
