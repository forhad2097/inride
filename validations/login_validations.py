"""Login page assertions."""

from __future__ import annotations

from config.roles import Role
from pages.login_page import LoginPage
from utils.logger import get_logger
from utils.verification import Verifier

log = get_logger(__name__)

#: Footer items expected on the login page, keyed by their stable test id.
#: Icon-only social links carry their accessible name in aria-label.
EXPECTED_FOOTER_ITEMS: tuple[tuple[str, str], ...] = (
    ("link-ai-terms", "Trade Agent AI Terms"),
    ("link-privacy", "Privacy Policy"),
    ("link-cookies", "Cookies Policy"),
    ("link-phone", "855-712-1112"),
    ("link-email", "Click here to email our sales team"),
    ("link-facebook", "Facebook"),
    ("link-instagram", "Instagram"),
    ("link-linkedin", "LinkedIn"),
    ("link-twitter", "X (Twitter)"),
)

TAGLINE = "AI-powered customer engagement management for automotive dealers"


class LoginPageValidations:
    """Every assertion is named so the report reads as a checklist."""

    def __init__(self, verify: Verifier, login_page: LoginPage, role: Role) -> None:
        self.verify = verify
        self.page_object = login_page
        self.prefix = f"{role.display_name} - Login Page"

    # --- branding ---------------------------------------------------
    def validate_branding(self) -> None:
        self.verify.visible(self.page_object.logo, f"{self.prefix} Logo is visible")
        self.verify.has_attribute(
            self.page_object.logo,
            "alt",
            "Trade Agent AI Logo",
            f"{self.prefix} Logo has the correct alt text",
        )
        self.verify.visible(self.page_object.tagline, f"{self.prefix} Heading is visible")
        self.verify.has_text(
            self.page_object.tagline,
            TAGLINE,
            f"{self.prefix} Heading text is '{TAGLINE}'",
        )

    # --- form -------------------------------------------------------
    def validate_login_form(self) -> None:
        self.verify.visible(
            self.page_object.email_input, f"{self.prefix} Email field is visible"
        )
        self.verify.visible(
            self.page_object.password_input, f"{self.prefix} Password field is visible"
        )
        self.verify.visible(
            self.page_object.forgot_password_link,
            f"{self.prefix} Forgot Password option is visible",
        )
        self.verify.has_text(
            self.page_object.forgot_password_link,
            "Forgot password?",
            f"{self.prefix} Forgot Password link text is correct",
        )
        self.verify.visible(
            self.page_object.login_button, f"{self.prefix} Login button is visible"
        )
        self.verify.has_text(
            self.page_object.login_button,
            "Log In",
            f"{self.prefix} Login button text is correct",
        )
        self.verify.visible(
            self.page_object.sso_login_button, f"{self.prefix} SSO Login option is visible"
        )
        self.verify.has_text(
            self.page_object.sso_login_button,
            "Log in with SSO",
            f"{self.prefix} SSO Login button text is correct",
        )
        self.verify.visible(
            self.page_object.google_login_button,
            f"{self.prefix} Google Login option is visible",
        )
        self.verify.has_text(
            self.page_object.google_login_button,
            "Log in with Google",
            f"{self.prefix} Google Login button text is correct",
        )

    # --- footer -----------------------------------------------------
    def validate_footer(self) -> list[dict[str, str]]:
        """Discover the footer dynamically, record what is there, then assert
        each expected item individually. Order is not assumed."""
        self.verify.visible(self.page_object.footer, f"{self.prefix} Footer is visible")

        found = self.page_object.visible_footer_items()
        names = [item["name"] for item in found if item["name"]]
        self.verify.record_info(
            f"{self.prefix} Footer items detected ({len(found)})",
            ", ".join(names),
        )
        log.info("footer items found: %s", names)

        for test_id, expected_name in EXPECTED_FOOTER_ITEMS:
            locator = self.page_object.footer_link(test_id)
            self.verify.visible(
                locator, f"{self.prefix} Footer item '{expected_name}' is visible"
            )

        detected_ids = {item["testId"] for item in found}

        def _assert_detected(test_id: str) -> None:
            assert test_id in detected_ids, f"{test_id} was not in the rendered footer"

        for test_id, expected_name in EXPECTED_FOOTER_ITEMS:
            self.verify.custom(
                f"{self.prefix} Footer item '{expected_name}' was detected dynamically",
                lambda t=test_id: _assert_detected(t),
                expected=f"{test_id} present in the rendered footer",
                actual="present" if test_id in detected_ids else "missing",
            )

        # Anything the application added that the expectation list does not
        # know about yet - reported, not failed, so the list can be extended.
        expected_ids = {test_id for test_id, _ in EXPECTED_FOOTER_ITEMS}
        unexpected = [i["name"] or i["testId"] for i in found if i["testId"] not in expected_ids]
        if unexpected:
            self.verify.record_info(
                f"{self.prefix} Additional footer items not yet in the expectation list",
                ", ".join(unexpected),
            )
        return found
