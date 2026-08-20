"""User roles and credentials.

Credentials are read from the environment (``.env``) and never hardcoded in a
test. ``Credentials.__repr__`` masks the password so it cannot leak into a
pytest failure line, a log record or an HTML report.

Adding a role later = add an enum member + two ``.env`` keys. No test changes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum

# Importing settings is what loads .env. Without this, importing config.roles on
# its own (a script, a REPL, a one-off check) silently reads an empty
# environment and reports every role as unconfigured.
from config import settings as _settings  # noqa: F401


class Role(str, Enum):
    PLATFORM_ADMIN = "PLATFORM_ADMIN"
    DEALER_ADMIN = "DEALER_ADMIN"
    USER = "USER"
    READ_ONLY_USER = "READ_ONLY_USER"

    @property
    def display_name(self) -> str:
        return self.value.replace("_", " ").title()


@dataclass(frozen=True)
class Credentials:
    role: Role
    username: str
    password: str

    def __repr__(self) -> str:  # keeps the password out of reports and logs
        return f"Credentials(role={self.role.value}, username={self.username!r}, password='***')"

    __str__ = __repr__


class MissingCredentialsError(RuntimeError):
    """Raised when a role is requested but its .env keys are not set."""


def credentials_for(role: Role) -> Credentials:
    """Resolve a role to its credentials from the environment.

    Looks up ``<ROLE>_USERNAME`` / ``<ROLE>_PASSWORD``, e.g.
    ``PLATFORM_ADMIN_USERNAME`` and ``PLATFORM_ADMIN_PASSWORD``.
    """
    username = os.getenv(f"{role.value}_USERNAME", "").strip()
    password = os.getenv(f"{role.value}_PASSWORD", "").strip()

    if not username or not password:
        raise MissingCredentialsError(
            f"Credentials for {role.value} are not configured. "
            f"Set {role.value}_USERNAME and {role.value}_PASSWORD in .env "
            f"(copy .env.example if you have not already)."
        )
    return Credentials(role=role, username=username, password=password)


def configured_roles() -> list[Role]:
    """Roles that currently have usable credentials - useful for future
    multi-role parametrisation without touching this module again."""
    available = []
    for role in Role:
        try:
            credentials_for(role)
        except MissingCredentialsError:
            continue
        available.append(role)
    return available
