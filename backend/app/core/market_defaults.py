"""The market a fresh PrimeCrest install serves: Pakistan, unless the operator says otherwise.

One place for the values a new workspace, account or project starts from when
nobody has chosen yet. Every value is read from the environment at call time,
so an operator deploying for another market overrides it without a code change:

==================================  ===================  ==========================
Environment variable                Default              Meaning
==================================  ===================  ==========================
``PRIMECREST_DEFAULT_COUNTRY``      ``PK``               ISO 3166-1 alpha-2
``PRIMECREST_DEFAULT_CURRENCY``     ``PKR``              ISO 4217
``PRIMECREST_DEFAULT_TIMEZONE``     ``Asia/Karachi``     IANA zone for new accounts
``PRIMECREST_DEFAULT_LOCALE``       ``en``               UI language (Urdu: ``ur``)
``PRIMECREST_DEFAULT_DATE_FORMAT``  ``DD/MM/YYYY``       numeric date order
``PRIMECREST_DEFAULT_PACK``         ``pakistan-pk``      regional pack the CLI opens
==================================  ===================  ==========================

An empty value counts as unset. The regional pack itself is still selected by
``OE_PACK`` / ``OE_PARTNER_PACK`` (see ``partner_pack.discovery``); this
module only says which slug a fresh install proposes.
"""

from __future__ import annotations

import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = [
    "DEFAULT_COUNTRY",
    "DEFAULT_CURRENCY",
    "DEFAULT_DATE_FORMAT",
    "DEFAULT_LOCALE",
    "DEFAULT_PACK",
    "DEFAULT_TIMEZONE",
    "SUGGESTED_LOCALES",
    "default_country",
    "default_currency",
    "default_date_format",
    "default_locale",
    "default_pack",
    "default_timezone",
]

DEFAULT_COUNTRY = "PK"
DEFAULT_CURRENCY = "PKR"
DEFAULT_TIMEZONE = "Asia/Karachi"
DEFAULT_LOCALE = "en"
DEFAULT_DATE_FORMAT = "DD/MM/YYYY"
DEFAULT_PACK = "pakistan-pk"

#: The UI languages a Pakistani workspace offers first, in this order.
SUGGESTED_LOCALES: tuple[str, ...] = ("en", "en-GB", "ur")


def _env(name: str, fallback: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or fallback


def default_country() -> str:
    """ISO 3166-1 alpha-2 country a fresh install serves (``PK``)."""
    return _env("PRIMECREST_DEFAULT_COUNTRY", DEFAULT_COUNTRY).upper()


def default_currency() -> str:
    """ISO 4217 currency a fresh install prices in (``PKR``)."""
    return _env("PRIMECREST_DEFAULT_CURRENCY", DEFAULT_CURRENCY).upper()


def default_timezone() -> str:
    """IANA time zone a new account starts in (``Asia/Karachi``).

    A value the platform's zone database does not know falls back to the
    built-in default rather than storing a zone nothing can convert with.
    """
    zone = _env("PRIMECREST_DEFAULT_TIMEZONE", DEFAULT_TIMEZONE)
    try:
        ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError):
        return DEFAULT_TIMEZONE
    return zone


def default_locale() -> str:
    """UI language a fresh install opens in (``en``; Urdu is ``ur``)."""
    return _env("PRIMECREST_DEFAULT_LOCALE", DEFAULT_LOCALE)


def default_date_format() -> str:
    """Numeric date order the market writes (``DD/MM/YYYY``)."""
    return _env("PRIMECREST_DEFAULT_DATE_FORMAT", DEFAULT_DATE_FORMAT)


def default_pack() -> str:
    """Regional pack slug a fresh CLI install activates (``pakistan-pk``)."""
    return _env("PRIMECREST_DEFAULT_PACK", DEFAULT_PACK)
