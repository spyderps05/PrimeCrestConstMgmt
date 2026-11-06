"""Ranking rules for rows that come from a country pack's schedules of rates.

Pure functions, no database. Both scorers use them: the lexical matcher behind
``POST /costs/match/`` (:mod:`app.modules.costs.matcher`) and cost-match runs
(:mod:`app.modules.cost_match`).

Three rules, each one small and explainable on its own:

* **Province first.** A Pakistan project is priced from its own province's
  schedule (Punjab MRS for Lahore, KP CSR for Peshawar), then from the national
  MES schedule, then from the other provinces. A province with no book yet
  (Sindh) falls back to MES first. Nothing is hidden: the preference only moves
  rows up or down the list.
* **Unwanted variants down.** A schedule prints "Dismantling cement concrete"
  and "Repair of cement concrete" next to the new work. Unless the line asks
  for dismantling, removal, demolition or repair, those rows are pushed down.
* **Units.** A row priced in a unit that converts to the line's unit (t and kg,
  m3 and cft) is kept and its conversion is stated; a row in a unit of another
  dimension (pcs for a m3 line) is pushed down.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from decimal import Decimal
from typing import Any

# ── Province of a project ───────────────────────────────────────────────────

#: Rank of a row's book relative to the project's province.
RANK_OWN_PROVINCE = 0
RANK_NATIONAL = 1
RANK_OTHER_PROVINCE = 2
RANK_UNKNOWN = 1

#: Score adjustment per rank. Small on purpose: it orders near-equal rows, it
#: does not turn a poor description match into a good one.
_PROVINCE_ADJUST: dict[int, float] = {
    RANK_OWN_PROVINCE: 0.04,
    RANK_NATIONAL: 0.0,
    RANK_OTHER_PROVINCE: -0.04,
}

PROVINCE_CODES: tuple[str, ...] = ("PK-PB", "PK-SD", "PK-KP", "PK-BA", "PK-IS", "PK-GB", "PK-JK")
_PROVINCE_CODES = frozenset(PROVINCE_CODES)

# Cities and province names that name a province in an address or a project
# title. Whole words only, so "Sindhi" in a firm name does not count.
_PLACE_TO_PROVINCE: dict[str, str] = {
    # Punjab
    "punjab": "PK-PB",
    "lahore": "PK-PB",
    "faisalabad": "PK-PB",
    "rawalpindi": "PK-PB",
    "multan": "PK-PB",
    "gujranwala": "PK-PB",
    "sialkot": "PK-PB",
    "bahawalpur": "PK-PB",
    "sargodha": "PK-PB",
    "sahiwal": "PK-PB",
    "sheikhupura": "PK-PB",
    "jhang": "PK-PB",
    "gujrat": "PK-PB",
    "kasur": "PK-PB",
    "okara": "PK-PB",
    "rahim yar khan": "PK-PB",
    "dera ghazi khan": "PK-PB",
    # Sindh
    "sindh": "PK-SD",
    "karachi": "PK-SD",
    "hyderabad": "PK-SD",
    "sukkur": "PK-SD",
    "larkana": "PK-SD",
    "nawabshah": "PK-SD",
    "mirpur khas": "PK-SD",
    # Khyber Pakhtunkhwa
    "khyber pakhtunkhwa": "PK-KP",
    "kpk": "PK-KP",
    "peshawar": "PK-KP",
    "mardan": "PK-KP",
    "abbottabad": "PK-KP",
    "swat": "PK-KP",
    "mingora": "PK-KP",
    "kohat": "PK-KP",
    "bannu": "PK-KP",
    "dera ismail khan": "PK-KP",
    "nowshera": "PK-KP",
    # Balochistan
    "balochistan": "PK-BA",
    "quetta": "PK-BA",
    "gwadar": "PK-BA",
    "turbat": "PK-BA",
    "khuzdar": "PK-BA",
    # Islamabad Capital Territory
    "islamabad": "PK-IS",
    # Gilgit-Baltistan and AJK
    "gilgit": "PK-GB",
    "skardu": "PK-GB",
    "muzaffarabad": "PK-JK",
}

_PLACE_RE = re.compile(
    r"\b(" + "|".join(re.escape(p) for p in sorted(_PLACE_TO_PROVINCE, key=len, reverse=True)) + r")\b",
    re.I,
)


def province_from_text(*texts: Any) -> str | None:
    """The first province any of ``texts`` names, as an ISO 3166-2 code.

    A text that is already a province code (``"PK-PB"``) answers itself.
    """
    for text in texts:
        if not isinstance(text, str) or not text.strip():
            continue
        code = text.strip().upper().replace("_", "-")
        if code in _PROVINCE_CODES:
            return code
        m = _PLACE_RE.search(text)
        if m:
            return _PLACE_TO_PROVINCE[m.group(1).lower()]
    return None


def province_for_project(project: Any) -> str | None:
    """The province a project's work is in, or ``None`` when it does not say.

    Read in order of how deliberate the statement is: the subdivision code,
    the structured address (region or state, then city), the project's region
    and metadata, and last its name ("House on a 10-marla plot, Lahore").
    """
    if project is None:
        return None
    sub = getattr(project, "subdivision_code", None)
    found = province_from_text(sub)
    if found:
        return found
    address = getattr(project, "address", None)
    if isinstance(address, Mapping):
        found = province_from_text(
            address.get("subdivision"),
            address.get("province"),
            address.get("state"),
            address.get("region"),
            address.get("city"),
            address.get("street"),
        )
        if found:
            return found
    meta = getattr(project, "metadata_", None)
    meta_texts: list[Any] = []
    if isinstance(meta, Mapping):
        meta_texts = [meta.get("province"), meta.get("subdivision"), meta.get("city"), meta.get("location")]
    return province_from_text(getattr(project, "region", None), *meta_texts, getattr(project, "name", None))


def book_region(item: Any) -> str | None:
    """The region a rate-book row's book is published for ("PK-PB", "PK"), else ``None``.

    Only rows loaded from a pack's schedule of rates carry it; any other row
    answers ``None`` and is never moved by the province rule.
    """
    if getattr(item, "source", None) != "rate_book":
        return None
    meta = getattr(item, "metadata_", None)
    if not isinstance(meta, Mapping):
        return None
    book = meta.get("rate_book")
    if not isinstance(book, Mapping):
        return None
    region = str(book.get("region") or "").strip().upper()
    return region or None


def book_rank(region: str | None, province: str | None) -> int:
    """Where a book sits for a project in ``province``: own, national, or another province."""
    if not province or not region:
        return RANK_UNKNOWN
    if region == province:
        return RANK_OWN_PROVINCE
    if region in _PROVINCE_CODES:
        return RANK_OTHER_PROVINCE
    # "PK", or anything that is not a province: a national schedule.
    return RANK_NATIONAL


def province_adjustment(region: str | None, province: str | None) -> float:
    """Score adjustment for a row of a book published for ``region``."""
    if not province or not region:
        return 0.0
    return _PROVINCE_ADJUST[book_rank(region, province)]


# ── Unwanted variants ───────────────────────────────────────────────────────

# A row *is* such a variant when it opens with the word ("Dismantling cement
# concrete", "Repair to plaster"); a word later in a new-work item ("including
# removal of surplus earth") is part of the work and does not count. A few
# phrasings mark a variant wherever they sit ("if fixed in repairs", "taking
# down and removing").
_VARIANT_RE = re.compile(r"\b(dismantl\w*|remov\w*|demoli\w*|repair\w*)", re.I)
_VARIANT_ANYWHERE_RE = re.compile(r"\b(in\s+repairs?|taking\s+(?:up|down)|dismantl\w*|demolition)\b", re.I)
_LEADING_WORDS = 6
# Words in a line that already ask for taking something away or mending it.
_QUERY_VARIANT_RE = re.compile(r"\b(dismantl\w*|remov\w*|demoli\w*|repair\w*|disposal|strip\w*|break\w* up)", re.I)

VARIANT_PENALTY = 0.75
"""Multiplier on a confidence when the row is a dismantling/repair variant the line did not ask for."""


def is_unwanted_variant(query: str | None, candidate: str | None) -> bool:
    """True when ``candidate`` is a dismantling, removal, demolition or repair item and ``query`` asks for none."""
    if not candidate:
        return False
    leading = " ".join(candidate.split()[:_LEADING_WORDS])
    if not (_VARIANT_RE.search(leading) or _VARIANT_ANYWHERE_RE.search(candidate)):
        return False
    return not (query and _QUERY_VARIANT_RE.search(query))


# ── Units ───────────────────────────────────────────────────────────────────

# How many of the base unit of its dimension one unit is. Only units a
# schedule of rates or a bill actually uses; anything else is unknown.
_UNIT_SCALE: dict[str, tuple[str, Decimal]] = {
    "kg": ("mass", Decimal("1")),
    "t": ("mass", Decimal("1000")),
    "ton": ("mass", Decimal("1000")),
    "tonne": ("mass", Decimal("1000")),
    "m": ("length", Decimal("1")),
    "rm": ("length", Decimal("1")),
    "lm": ("length", Decimal("1")),
    "rmt": ("length", Decimal("1")),
    "rft": ("length", Decimal("0.3048")),
    "ft": ("length", Decimal("0.3048")),
    "m2": ("area", Decimal("1")),
    "sqm": ("area", Decimal("1")),
    "sft": ("area", Decimal("0.09290304")),
    "sqft": ("area", Decimal("0.09290304")),
    "m3": ("volume", Decimal("1")),
    "cum": ("volume", Decimal("1")),
    "cft": ("volume", Decimal("0.028316846592")),
    "l": ("volume", Decimal("0.001")),
    "pcs": ("count", Decimal("1")),
    "pc": ("count", Decimal("1")),
    "no": ("count", Decimal("1")),
    "nr": ("count", Decimal("1")),
    "each": ("count", Decimal("1")),
    "ea": ("count", Decimal("1")),
    "lsum": ("sum", Decimal("1")),
    "ls": ("sum", Decimal("1")),
    "job": ("sum", Decimal("1")),
    "hr": ("time", Decimal("1")),
    "h": ("time", Decimal("1")),
    "day": ("time", Decimal("8")),
}

UNIT_SAME = "same"
UNIT_CONVERTIBLE = "convertible"
UNIT_INCOMPATIBLE = "incompatible"
UNIT_UNKNOWN = "unknown"

#: Score adjustment per unit relation for the lexical scorer.
UNIT_ADJUST: dict[str, float] = {
    UNIT_SAME: 0.10,
    UNIT_CONVERTIBLE: 0.06,
    UNIT_INCOMPATIBLE: -0.15,
    UNIT_UNKNOWN: 0.0,
}


def _unit_key(unit: str | None) -> str:
    if not unit:
        return ""
    folded = unit.strip().lower().replace("²", "2").replace("³", "3").replace(".", "")
    return re.sub(r"[\s\-/]", "", folded)


def unit_relation(query_unit: str | None, item_unit: str | None) -> str:
    """``same``, ``convertible``, ``incompatible`` or ``unknown`` for two units."""
    a, b = _unit_key(query_unit), _unit_key(item_unit)
    if not a or not b:
        return UNIT_UNKNOWN
    if a == b:
        return UNIT_SAME
    sa, sb = _UNIT_SCALE.get(a), _UNIT_SCALE.get(b)
    if sa is None or sb is None:
        return UNIT_UNKNOWN
    if sa[0] != sb[0]:
        return UNIT_INCOMPATIBLE
    if sa[1] == sb[1]:
        return UNIT_SAME
    # A day is not a fixed number of hours on every site: no conversion.
    if sa[0] == "time":
        return UNIT_UNKNOWN
    return UNIT_CONVERTIBLE


def unit_factor(query_unit: str | None, item_unit: str | None) -> Decimal | None:
    """How many ``item_unit`` make one ``query_unit`` (1 t = 1000 kg), when they convert."""
    if unit_relation(query_unit, item_unit) not in (UNIT_SAME, UNIT_CONVERTIBLE):
        return None
    a, b = _UNIT_SCALE.get(_unit_key(query_unit)), _UNIT_SCALE.get(_unit_key(item_unit))
    if a is None or b is None:
        return Decimal("1")
    return a[1] / b[1]


def converted_rate(rate: Decimal | str | float | None, query_unit: str | None, item_unit: str | None) -> Decimal | None:
    """The item's rate per ``query_unit``: a 250 PKR/kg rate is 250,000 PKR/t."""
    factor = unit_factor(query_unit, item_unit)
    if factor is None or rate is None:
        return None
    try:
        return Decimal(str(rate)) * factor
    except (ArithmeticError, ValueError):
        return None


def conversion_note(query_unit: str | None, item_unit: str | None) -> str:
    """ "1 t = 1000 kg" for a convertible pair, empty otherwise."""
    if unit_relation(query_unit, item_unit) != UNIT_CONVERTIBLE:
        return ""
    factor = unit_factor(query_unit, item_unit)
    if factor is None:
        return ""
    shown = format(factor.normalize(), "f") if factor == factor.to_integral() else f"{factor:.6g}"
    return f"1 {query_unit} = {shown} {item_unit}"


__all__ = [
    "PROVINCE_CODES",
    "RANK_NATIONAL",
    "RANK_OTHER_PROVINCE",
    "RANK_OWN_PROVINCE",
    "UNIT_ADJUST",
    "UNIT_CONVERTIBLE",
    "UNIT_INCOMPATIBLE",
    "UNIT_SAME",
    "UNIT_UNKNOWN",
    "VARIANT_PENALTY",
    "book_rank",
    "book_region",
    "conversion_note",
    "converted_rate",
    "is_unwanted_variant",
    "province_adjustment",
    "province_for_project",
    "province_from_text",
    "unit_factor",
    "unit_relation",
]
