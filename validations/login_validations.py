"""Login page assertions.

Grouped to mirror the page: branding, login form, password visibility, footer
logo, legal, contact info, social media, copyright.

Expected values come from ``config/login_page.py``; locators come from
``pages/login_page.py``. Nothing in this module knows a selector.

The password is treated as a secret throughout: it is never placed in an
assertion description, an expected/actual value, or an AssertionError message.
"""

from __future__ import annotations

from config import login_page as copy
from config.roles import Role
from pages.login_page import LoginPage
from utils.logger import get_logger
from utils.verification import Verifier

log = get_logger(__name__)


class LoginPageValidations:
    """Every assertion is named so the report reads as a checklist."""

    def __init__(self, verify: Verifier, login_page: LoginPage, role: Role) -> None:
        self.verify = verify
        self.page_object = login_page
        self.prefix = f"{role.display_name} - Login Page"

    # ================================================== branding
    def validate_branding(self) -> None:
        self.verify.visible(self.page_object.logo, f"{self.prefix} Logo is visible")
        self.verify.has_attribute(
            self.page_object.logo,
            "alt",
            copy.LOGO_ALT,
            f"{self.prefix} Logo has the correct alt text",
        )
        self.verify.visible(self.page_object.tagline, f"{self.prefix} Heading is visible")
        self.verify.has_text(
            self.page_object.tagline,
            copy.TAGLINE,
            f"{self.prefix} Heading text is '{copy.TAGLINE}'",
        )

    # ================================================ login form
    def validate_login_form(self) -> None:
        """Every control a user needs before authenticating."""
        # --- title ---
        self.verify.visible(
            self.page_object.login_title,
            f"{self.prefix} '{copy.LOGIN_TITLE}' title is visible",
        )
        self.verify.has_text(
            self.page_object.login_title,
            copy.LOGIN_TITLE,
            f"{self.prefix} Title text is exactly '{copy.LOGIN_TITLE}'",
        )

        # --- field labels ---
        self.verify.visible(
            self.page_object.email_label,
            f"{self.prefix} '{copy.EMAIL_LABEL}' label is visible above the email field",
        )
        self.verify.has_text(
            self.page_object.email_label,
            copy.EMAIL_LABEL,
            f"{self.prefix} Email label text is exactly '{copy.EMAIL_LABEL}'",
        )
        self.verify.visible(
            self.page_object.password_label,
            f"{self.prefix} '{copy.PASSWORD_LABEL}' label is visible above the password field",
        )
        self.verify.has_text(
            self.page_object.password_label,
            copy.PASSWORD_LABEL,
            f"{self.prefix} Password label text is exactly '{copy.PASSWORD_LABEL}'",
        )

        # --- inputs ---
        self.verify.visible(
            self.page_object.email_input, f"{self.prefix} Email field is visible"
        )
        self.verify.visible(
            self.page_object.password_input, f"{self.prefix} Password field is visible"
        )
        self.verify.has_attribute(
            self.page_object.password_input,
            "type",
            copy.MASKED_TYPE,
            f"{self.prefix} Password field is masked before anything is typed",
        )

        # --- actions ---
        self.verify.visible(
            self.page_object.forgot_password_link,
            f"{self.prefix} Forgot Password option is visible",
        )
        self.verify.has_text(
            self.page_object.forgot_password_link,
            copy.FORGOT_PASSWORD_TEXT,
            f"{self.prefix} Forgot Password link text is correct",
        )
        self.verify.visible(
            self.page_object.login_button, f"{self.prefix} Login button is visible"
        )
        self.verify.has_text(
            self.page_object.login_button,
            copy.LOGIN_BUTTON_TEXT,
            f"{self.prefix} Login button text is correct",
        )
        self.verify.visible(
            self.page_object.sso_login_button, f"{self.prefix} SSO Login option is visible"
        )
        self.verify.has_text(
            self.page_object.sso_login_button,
            copy.SSO_BUTTON_TEXT,
            f"{self.prefix} SSO Login button text is correct",
        )
        self.verify.visible(
            self.page_object.google_login_button,
            f"{self.prefix} Google Login option is visible",
        )
        self.verify.has_text(
            self.page_object.google_login_button,
            copy.GOOGLE_BUTTON_TEXT,
            f"{self.prefix} Google Login button text is correct",
        )
        self.verify.visible(
            self.page_object.show_password_button,
            f"{self.prefix} '{copy.SHOW_PASSWORD_LABEL}' control is visible",
        )

    # ============================================== footer: logo
    def validate_footer_logo(self) -> None:
        self.verify.visible(self.page_object.footer, f"{self.prefix} Footer is visible")
        self.verify.visible(
            self.page_object.footer_logo, f"{self.prefix} Footer logo is visible"
        )
        self.verify.has_attribute(
            self.page_object.footer_logo,
            "alt",
            copy.FOOTER_LOGO_ALT,
            f"{self.prefix} Footer logo alt text is '{copy.FOOTER_LOGO_ALT}'",
        )

    # ============================================= footer: legal
    def validate_legal_section(self) -> None:
        self.verify.visible(
            self.page_object.legal_section,
            f"{self.prefix} '{copy.LEGAL_SECTION}' section heading is visible",
        )
        self.verify.has_text(
            self.page_object.legal_section,
            copy.LEGAL_SECTION,
            f"{self.prefix} Legal section heading text is exactly '{copy.LEGAL_SECTION}'",
        )
        for link in copy.LEGAL_LINKS:
            locator = self.page_object.footer_link(link.test_id)
            self.verify.visible(
                locator, f"{self.prefix} Legal link '{link.name}' is visible"
            )
            self.verify.has_text(
                locator,
                link.name,
                f"{self.prefix} Legal link text is '{link.name}'",
            )
            if link.href:
                self.verify.has_attribute(
                    locator,
                    "href",
                    link.href,
                    f"{self.prefix} Legal link '{link.name}' points to {link.href}",
                )

    # ====================================== footer: contact info
    def validate_contact_info_section(self) -> None:
        self.verify.visible(
            self.page_object.contact_info_section,
            f"{self.prefix} '{copy.CONTACT_SECTION}' section heading is visible",
        )
        self.verify.has_text(
            self.page_object.contact_info_section,
            copy.CONTACT_SECTION,
            f"{self.prefix} Contact section heading text is exactly '{copy.CONTACT_SECTION}'",
        )

        # --- address ---
        self.verify.visible(self.page_object.address, f"{self.prefix} Address is visible")
        self.verify.has_text(
            self.page_object.address,
            copy.ADDRESS_TEXT,
            f"{self.prefix} Address text is '{copy.ADDRESS_TEXT}'",
        )

        # --- phone ---
        self.verify.visible(
            self.page_object.phone_link, f"{self.prefix} Phone number is visible"
        )
        self.verify.has_text(
            self.page_object.phone_link,
            copy.PHONE_TEXT,
            f"{self.prefix} Phone number text is '{copy.PHONE_TEXT}'",
        )
        self.verify.has_attribute(
            self.page_object.phone_link,
            "href",
            copy.PHONE_HREF,
            f"{self.prefix} Phone link dials {copy.PHONE_TEXT}",
        )

        # --- email: the visible text is a call to action, the address is the href ---
        self.verify.visible(
            self.page_object.email_link, f"{self.prefix} Sales email link is visible"
        )
        self.verify.has_text(
            self.page_object.email_link,
            copy.EMAIL_LINK_TEXT,
            f"{self.prefix} Sales email link text is '{copy.EMAIL_LINK_TEXT}'",
        )
        self.verify.has_attribute(
            self.page_object.email_link,
            "href",
            copy.EMAIL_HREF,
            f"{self.prefix} Sales email link points to {copy.EMAIL_HREF}",
        )

    # ====================================== footer: social media
    def validate_social_links(self) -> None:
        """Icon-only links. They expose their accessible name via aria-label,
        so every one is reachable with a stable, accessible locator."""
        for link in copy.SOCIAL_LINKS:
            locator = self.page_object.footer_link(link.test_id)
            self.verify.visible(
                locator, f"{self.prefix} Social icon '{link.name}' is visible"
            )
            self.verify.has_attribute(
                locator,
                "aria-label",
                link.name,
                f"{self.prefix} Social icon '{link.name}' has an accessible name",
            )
            if link.href:
                self.verify.has_attribute(
                    locator,
                    "href",
                    link.href,
                    f"{self.prefix} Social icon '{link.name}' points to {link.href}",
                )
        self.verify.record_info(
            f"{self.prefix} Social icon locator strategy",
            f"all {len(copy.SOCIAL_LINKS)} icons expose a data-testid and an aria-label - "
            f"no CSS or XPath fallback was needed",
        )

    # ========================================= footer: copyright
    def validate_copyright(self) -> None:
        self.verify.visible(
            self.page_object.copyright_text, f"{self.prefix} Copyright notice is visible"
        )
        self.verify.has_text(
            self.page_object.copyright_text,
            copy.COPYRIGHT.value,
            f"{self.prefix} Copyright text is exactly '{copy.COPYRIGHT.value}'",
        )
        if copy.COPYRIGHT.deviates:
            self.verify.record_info(
                f"{self.prefix} Copyright wording differs from the requirement document",
                f"requirement asked for '{copy.COPYRIGHT.spec_text}', "
                f"application renders '{copy.COPYRIGHT.value}'",
            )

    # ================================= footer: dynamic inventory
    def validate_footer_inventory(self) -> list[dict[str, str]]:
        """Discover what the footer actually renders, then confirm every
        expected link was among it. Order is not assumed."""
        found = self.page_object.visible_footer_items()
        names = [item["name"] for item in found if item["name"]]
        self.verify.record_info(
            f"{self.prefix} Footer links detected ({len(found)})", ", ".join(names)
        )
        log.info("footer links found: %s", names)

        detected_ids = {item["testId"] for item in found}

        def _assert_detected(test_id: str) -> None:
            assert test_id in detected_ids, f"{test_id} was not in the rendered footer"

        for link in copy.ALL_FOOTER_LINKS:
            self.verify.custom(
                f"{self.prefix} Footer link '{link.name}' was detected dynamically",
                lambda t=link.test_id: _assert_detected(t),
                expected=f"{link.test_id} present in the rendered footer",
                actual="present" if link.test_id in detected_ids else "missing",
            )

        expected_ids = {link.test_id for link in copy.ALL_FOOTER_LINKS}
        unexpected = [
            i["name"] or i["testId"] for i in found if i["testId"] not in expected_ids
        ]
        if unexpected:
            self.verify.record_info(
                f"{self.prefix} Additional footer links not yet in the expectation list",
                ", ".join(unexpected),
            )
        return found

    def validate_footer(self) -> list[dict[str, str]]:
        """The complete footer, section by section."""
        self.validate_footer_logo()
        self.validate_legal_section()
        self.validate_contact_info_section()
        self.validate_social_links()
        self.validate_copyright()
        return self.validate_footer_inventory()

    # ============================= password visibility (functional)
    def validate_password_is_masked(self, expected_password: str, *, stage: str) -> None:
        """The field hides the value, and the value itself is intact.

        ``expected_password`` is compared but never reported: descriptions and
        expected/actual values only ever say 'hidden' or 'unchanged'.
        """
        self.verify.has_attribute(
            self.page_object.password_input,
            "type",
            copy.MASKED_TYPE,
            f"{self.prefix} Password is masked {stage}",
        )
        field_type = self.page_object.password_field_type()
        self.verify.custom(
            f"{self.prefix} Password is not rendered as plain text {stage}",
            lambda: _assert_not_plain_text(field_type),
            expected=f"input type == '{copy.MASKED_TYPE}'",
            actual=f"input type == '{field_type}'",
        )
        self._assert_value_intact(expected_password, stage=stage)

    def validate_password_is_revealed(self, expected_password: str) -> None:
        self.verify.has_attribute(
            self.page_object.password_input,
            "type",
            copy.REVEALED_TYPE,
            f"{self.prefix} Password is revealed after clicking "
            f"'{copy.SHOW_PASSWORD_LABEL}'",
        )
        self._assert_value_intact(expected_password, stage="while revealed")

    def validate_toggle_offers_hide(self) -> None:
        """The control flips to the opposite affordance once the password shows."""
        self.verify.visible(
            self.page_object.hide_password_button,
            f"{self.prefix} Control changes to '{copy.HIDE_PASSWORD_LABEL}' "
            f"once the password is visible",
        )
        self.verify.has_count(
            self.page_object.show_password_button,
            0,
            f"{self.prefix} '{copy.SHOW_PASSWORD_LABEL}' control is no longer offered "
            f"while the password is visible",
        )

    def validate_toggle_offers_show(self) -> None:
        self.verify.visible(
            self.page_object.show_password_button,
            f"{self.prefix} Control changes back to '{copy.SHOW_PASSWORD_LABEL}' "
            f"once the password is hidden again",
        )

    def _assert_value_intact(self, expected_password: str, *, stage: str) -> None:
        matches = self.page_object.entered_password_matches(expected_password)
        self.verify.custom(
            f"{self.prefix} Entered password value is unchanged {stage}",
            lambda: _assert_value_matches(matches),
            expected="the typed value is still in the field (value hidden)",
            actual="unchanged" if matches else "CHANGED",
        )


# --- module-level helpers: kept free of the secret itself ------------
def _assert_not_plain_text(field_type: str) -> None:
    assert field_type == copy.MASKED_TYPE, (
        f"password field type is {field_type!r}, so the value is readable on screen"
    )


def _assert_value_matches(matches: bool) -> None:
    assert matches, "the password field value changed during the show/hide cycle"
