"""A fresh PrimeCrest install defaults to the Pakistan market, and every default is env-overridable."""

from __future__ import annotations

import pytest

from app.core import market_defaults as md


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "PRIMECREST_DEFAULT_COUNTRY",
        "PRIMECREST_DEFAULT_CURRENCY",
        "PRIMECREST_DEFAULT_TIMEZONE",
        "PRIMECREST_DEFAULT_LOCALE",
        "PRIMECREST_DEFAULT_DATE_FORMAT",
        "PRIMECREST_DEFAULT_PACK",
    ):
        monkeypatch.delenv(name, raising=False)


def test_defaults_are_pakistan() -> None:
    assert md.default_country() == "PK"
    assert md.default_currency() == "PKR"
    assert md.default_timezone() == "Asia/Karachi"
    assert md.default_locale() == "en"
    assert md.default_date_format() == "DD/MM/YYYY"
    assert md.default_pack() == "pakistan-pk"
    assert "ur" in md.SUGGESTED_LOCALES


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRIMECREST_DEFAULT_COUNTRY", "ae")
    monkeypatch.setenv("PRIMECREST_DEFAULT_CURRENCY", "aed")
    monkeypatch.setenv("PRIMECREST_DEFAULT_TIMEZONE", "Asia/Dubai")
    monkeypatch.setenv("PRIMECREST_DEFAULT_PACK", "uae-ae")
    assert md.default_country() == "AE"
    assert md.default_currency() == "AED"
    assert md.default_timezone() == "Asia/Dubai"
    assert md.default_pack() == "uae-ae"


def test_blank_or_unknown_values_fall_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRIMECREST_DEFAULT_CURRENCY", "   ")
    monkeypatch.setenv("PRIMECREST_DEFAULT_TIMEZONE", "Not/AZone")
    assert md.default_currency() == "PKR"
    assert md.default_timezone() == "Asia/Karachi"


def test_new_user_starts_in_market_timezone() -> None:
    from app.modules.users.models import User

    column_default = User.__table__.c.timezone.default
    assert column_default is not None
    assert column_default.arg.__name__ == "default_timezone"
    assert User.__table__.c.timezone.server_default.arg == "UTC"


def test_pakistan_demos_are_the_default_workspace() -> None:
    from app.core.demo_projects import DEMO_TEMPLATES, PACK_DEMO_PROJECT, PRODUCT_DEMO_IDS

    assert set(PRODUCT_DEMO_IDS) == {"lahore-house", "school-karachi", "bhu-punjab", "faisalabad-road"}
    assert all(demo_id in DEMO_TEMPLATES for demo_id in PRODUCT_DEMO_IDS)
    assert PACK_DEMO_PROJECT["pakistan-pk"] in PRODUCT_DEMO_IDS
