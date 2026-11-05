# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""Defaults that apply only while the Pakistan pack is the active pack.

A German or Gulf workspace that has not selected this pack keeps its own
currency and classification. An explicit value the user typed is kept.
"""

from __future__ import annotations

__all__ = ["apply_project_defaults", "currency_for_new_row", "pakistan_pack_active"]


def pakistan_pack_active() -> bool:
    try:
        from app.core.partner_pack.discovery import get_active_pack

        pack = get_active_pack()
    except Exception:  # noqa: BLE001 - a missing pack must not block a new row
        return False
    return bool(pack and pack.slug == "pakistan-pk")


def currency_for_new_row(currency: str) -> str:
    """PKR for a new tender or supplier row that still carries the old EUR default."""
    if pakistan_pack_active() and (currency or "").strip() in ("", "EUR"):
        return "PKR"
    return currency


def apply_project_defaults(
    currency: str,
    region: str,
    classification_standard: str,
    locale: str,
) -> tuple[str, str, str, str]:
    """Fill a blank new project. A value the caller already set is left as it is."""
    if not pakistan_pack_active():
        return currency, region, classification_standard, locale
    if not (currency or "").strip():
        currency = "PKR"
    if not (region or "").strip():
        region = "Pakistan"
    if not (classification_standard or "").strip():
        classification_standard = "masterformat"
    if not (locale or "").strip():
        locale = "en"
    return currency, region, classification_standard, locale
