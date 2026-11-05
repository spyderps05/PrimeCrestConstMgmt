"""Punjab rate-book importer and the Pakistan pack defaults."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.partner_pack.pakistan_defaults import apply_project_defaults, currency_for_new_row
from app.core.punjab_mrs import import_mrs_csv

_ROOT = Path(__file__).resolve().parents[3]
_HEADER = (
    "district,period,chapter,item_number,description,unit,labour_rate,composite_rate,"
    "material_rate,equipment_rate,specification_number,source_url\n"
)


def test_official_row_is_kept() -> None:
    text = _HEADER + (
        "Lahore,January-June 2025,7,7.1,Brick masonry,m3,100,900,700,100,7.1,"
        "https://finance.punjab.gov.pk/input-rates\n"
    )
    rows = import_mrs_csv(text)
    assert rows[0]["district"] == "Lahore"
    assert rows[0]["chapter"] == "7"
    assert rows[0]["labour_rate"] == "100"
    assert rows[0]["composite_rate"] == "900"


def test_third_party_dump_is_refused() -> None:
    text = _HEADER + (
        "Lahore,January-June 2025,7,7.1,Brick masonry,m3,100,900,,,7.1,"
        "https://example.com/rates\n"
    )
    with pytest.raises(ValueError, match="Third-party"):
        import_mrs_csv(text)


def test_rate_book_lists_27_chapters_and_two_districts() -> None:
    path = _ROOT / "packs/pakistan-pk/src/openconstructionerp_pakistan_pk/rates.json"
    book = json.loads(path.read_text(encoding="utf-8"))
    assert [chapter["number"] for chapter in book["chapters"]] == list(range(1, 28))
    assert [row["district"] for row in book["districts"]] == ["Lahore", "Faisalabad"]
    assert book["districts"][0]["items"] == []
    assert "finance.punjab.gov.pk" in book["input_rates_url"]


def test_new_row_defaults_follow_the_active_pack(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.core.partner_pack.pakistan_defaults.pakistan_pack_active",
        lambda: True,
    )
    assert currency_for_new_row("EUR") == "PKR"
    assert currency_for_new_row("USD") == "USD"
    currency, region, standard, locale = apply_project_defaults("", "", "", "")
    assert (currency, region, standard, locale) == ("PKR", "Pakistan", "masterformat", "en")
    kept = apply_project_defaults("EUR", "Sindh", "din276", "ur")
    assert kept == ("EUR", "Sindh", "din276", "ur")


def test_defaults_stay_put_when_the_pack_is_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.core.partner_pack.pakistan_defaults.pakistan_pack_active",
        lambda: False,
    )
    assert currency_for_new_row("EUR") == "EUR"
    assert apply_project_defaults("", "", "", "en") == ("", "", "", "en")
