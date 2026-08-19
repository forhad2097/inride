"""Expected content of the pre-login page: branding, form, and footer.

Data only - no locators and no logic. ``pages/login_page.py`` knows *how* to
find these things; this module records *what* must be there, so a wording change
in the application is a one-line edit here.

Where the requirement document asked for different wording than the application
renders, ``spec_text`` records the requested wording. The suite asserts the
**actual** text and reports the deviation, rather than silently passing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FooterLink:
    """One footer link, identified by its stable test id."""

    test_id: str
    #: accessible name - link text, or aria-label for an icon-only link
    name: str
    #: expected href, when it is part of the requirement
    href: str | None = None


@dataclass(frozen=True)
class ExpectedCopy:
    """A piece of static copy, plus the wording the requirement asked for."""

    value: str
    label: str
    spec_text: str | None = None

    @property
    def deviates(self) -> bool:
        return self.spec_text is not None and self.spec_text != self.value


# --------------------------------------------------------------- branding
LOGO_ALT = "Trade Agent AI Logo"
TAGLINE = "AI-powered customer engagement management for automotive dealers"

# ------------------------------------------------------------- login form
LOGIN_TITLE = "Log In"
EMAIL_LABEL = "Email"
PASSWORD_LABEL = "Password"
LOGIN_BUTTON_TEXT = "Log In"
FORGOT_PASSWORD_TEXT = "Forgot password?"
SSO_BUTTON_TEXT = "Log in with SSO"
GOOGLE_BUTTON_TEXT = "Log in with Google"

# ------------------------------------------------- password visibility
SHOW_PASSWORD_LABEL = "Show password"
HIDE_PASSWORD_LABEL = "Hide password"
#: the input's ``type`` while the password is masked / revealed
MASKED_TYPE = "password"
REVEALED_TYPE = "text"

# ------------------------------------------------------------------ footer
FOOTER_LOGO_ALT = "Trade Agent AI"

LEGAL_SECTION = "Legal"
LEGAL_LINKS: tuple[FooterLink, ...] = (
    FooterLink("link-ai-terms", "Trade Agent AI Terms",
               "https://inride.com/trage-agent-ai-terms/"),
    FooterLink("link-privacy", "Privacy Policy",
               "https://inride.com/privacy-policy/"),
    FooterLink("link-cookies", "Cookies Policy",
               "https://inride.com/cookies-policy/"),
)

#: the application renders "Contact Info" - not "Contact Information"
CONTACT_SECTION = "Contact Info"
ADDRESS_TEXT = "3111 Automobile Blvd, Silver Spring, MD 20904"
PHONE_TEXT = "855-712-1112"
PHONE_HREF = "tel:855-712-1112"
#: the link shows a call to action, not the address itself
EMAIL_LINK_TEXT = "Click here to email our sales team"
EMAIL_HREF = "mailto:tradeagentai@inride.com"

CONTACT_ITEMS: tuple[FooterLink, ...] = (
    FooterLink("text-address", ADDRESS_TEXT),
    FooterLink("link-phone", PHONE_TEXT, PHONE_HREF),
    FooterLink("link-email", EMAIL_LINK_TEXT, EMAIL_HREF),
)

#: icon-only links - they carry their accessible name in aria-label, so a
#: stable, accessible locator is available and no CSS/XPath is needed
SOCIAL_LINKS: tuple[FooterLink, ...] = (
    FooterLink("link-facebook", "Facebook", "https://www.facebook.com/inrideapp/"),
    FooterLink("link-instagram", "Instagram", "https://www.instagram.com/inrideapp/"),
    FooterLink("link-linkedin", "LinkedIn", "https://www.linkedin.com/company/inride"),
    FooterLink("link-twitter", "X (Twitter)", "https://x.com/Inrideapp"),
)

#: The requirement asked for "Copyright 2026, Inright LLC, All Rights Reserved".
#: The application renders a (c) symbol, no commas, a full stop, and spells the
#: company "Inride" - which matches the domain, so the requirement's "Inright"
#: looks like a typo. Asserted as rendered; the difference is reported.
COPYRIGHT = ExpectedCopy(
    value="\u00a9 Copyright 2026 Inride LLC. All Rights Reserved.",
    label="Copyright notice",
    spec_text="Copyright 2026, Inright LLC, All Rights Reserved",
)

#: every footer link that must be present, in one list for the dynamic sweep
ALL_FOOTER_LINKS: tuple[FooterLink, ...] = LEGAL_LINKS + CONTACT_ITEMS[1:] + SOCIAL_LINKS
