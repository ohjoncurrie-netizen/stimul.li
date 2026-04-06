from __future__ import annotations

import os
import re
import sys
from urllib.parse import urlparse


REQUIRED_ENV_VARS = ("OPENAI_API_KEY", "STRIPE_API_KEY", "DATABASE_URL")
OPENAI_KEY_PATTERN = re.compile(r"^sk-[A-Za-z0-9_\-]+$")
STRIPE_KEY_PATTERN = re.compile(r"^sk_(test|live)_[A-Za-z0-9]+$")
POSTGRES_SCHEMES = {"postgresql", "postgresql+psycopg"}


def _validate_openai_key(value: str) -> str | None:
    if not OPENAI_KEY_PATTERN.match(value):
        return "OPENAI_API_KEY must start with 'sk-' and contain only valid key characters."
    return None


def _validate_stripe_key(value: str) -> str | None:
    if not STRIPE_KEY_PATTERN.match(value):
        return "STRIPE_API_KEY must look like a Stripe secret key such as 'sk_live_...' or 'sk_test_...'."
    return None


def _validate_database_url(value: str) -> str | None:
    parsed = urlparse(value)
    if parsed.scheme not in POSTGRES_SCHEMES:
        return "DATABASE_URL must use the PostgreSQL SQLAlchemy dialect, for example 'postgresql+psycopg://...'."
    if not parsed.hostname:
        return "DATABASE_URL must include a database host."
    if not parsed.username:
        return "DATABASE_URL must include a database username."
    if not parsed.password:
        return "DATABASE_URL must include a database password."
    if not parsed.path or parsed.path == "/":
        return "DATABASE_URL must include a database name."
    return None


def validate_environment() -> list[str]:
    errors: list[str] = []

    for var_name in REQUIRED_ENV_VARS:
        value = os.getenv(var_name, "").strip()
        if not value:
            errors.append(f"{var_name} is required but not set.")
            continue

        if var_name == "OPENAI_API_KEY":
            error = _validate_openai_key(value)
        elif var_name == "STRIPE_API_KEY":
            error = _validate_stripe_key(value)
        else:
            error = _validate_database_url(value)

        if error:
            errors.append(error)

    return errors


def main() -> int:
    errors = validate_environment()
    if errors:
        for error in errors:
            print(f"ENV VALIDATION ERROR: {error}", file=sys.stderr)
        return 1

    print("Environment validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
