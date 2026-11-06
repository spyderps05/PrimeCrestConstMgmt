# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""Pakistani income tax withheld under section 153(1), one payee class at a time.

The rows come from two FBR rate cards (tax years 2026 and 2027), so every
case below is asked on a date in each window. The class matrix is the point:
a company and an individual pay different rates, and a payee off the Active
Taxpayer List pays double, so the wrong row always gives a different amount.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from app.core.payment_taxes import (
    Choice,
    PaymentTaxInput,
    categories,
    compute_payment_taxes,
    data_pk,
    rows_for,
    validate_rows,
)
from app.core.payment_taxes.tables import countries_with_rows, lookup
from app.modules.contracts.hakedis_layout import (
    DEFAULT_LAYOUTS,
    OFFICIAL_FORM_COUNTRIES,
    has_layout,
    resolve_settings,
)
from app.modules.tax_withholding.data import regime_by_scheme

D = Decimal
TY2026 = date(2026, 3, 15)
TY2027 = date(2026, 11, 6)
NA = Choice("not_applicable", reason="not used here")

#: (code, TY2026 rate, TY2027 rate), straight off the two cards.
EXPECTED: tuple[tuple[str, str, str], ...] = (
    ("PK_153_1C_COMPANY_ATL", "7.5", "7.5"),
    ("PK_153_1C_COMPANY_NON_ATL", "15", "15"),
    ("PK_153_1C_OTHER_ATL", "8", "8"),
    ("PK_153_1C_OTHER_NON_ATL", "16", "16"),
    ("PK_153_1A_COMPANY_ATL", "5", "5"),
    ("PK_153_1A_COMPANY_NON_ATL", "10", "10"),
    ("PK_153_1A_OTHER_ATL", "5.5", "5.5"),
    ("PK_153_1A_OTHER_NON_ATL", "11", "11"),
    ("PK_153_1B_CERTAIN_ATL", "6", "7"),
    ("PK_153_1B_CERTAIN_NON_ATL", "12", "14"),
    ("PK_153_1B_OTHER_ATL", "15", "14"),
    ("PK_153_1B_OTHER_NON_ATL", "30", "28"),
)


def _inp(code: str, on: date, net: str = "1000000.00", vat: str | None = "16") -> PaymentTaxInput:
    return PaymentTaxInput(
        country_code="PK",
        currency="PKR",
        on=on,
        net_amount=D(net),
        vat_rate_pct=D(vat) if vat is not None else None,
        vat_withholding=NA,
        income_withholding=Choice("selected", code),
        stamp_duty=NA,
        buyer_is_designated=True,
    )


# ── The table ────────────────────────────────────────────────────────────────


def test_pk_is_a_country_with_rows_and_the_table_is_sound() -> None:
    assert "PK" in countries_with_rows()
    assert validate_rows(rows_for("PK")) == []
    for row in data_pk.ROWS:
        assert row.kind == "income_withholding"
        assert row.review_status == "unconfirmed"
        assert row.source_url.startswith("https://download1.fbr.gov.pk/Docs/")
        assert row.read_date == "2026-11-06"
        assert set(row.labels) == {"en", "ur"}
        assert set(row.conditions) == {"en", "ur"}


def test_the_two_tax_years_are_windows_that_meet_without_overlapping() -> None:
    starts = {row.effective_from for row in data_pk.ROWS}
    assert starts == {date(2025, 7, 1), date(2026, 7, 1)}
    for row in data_pk.ROWS:
        if row.effective_from == date(2025, 7, 1):
            assert row.effective_to == date(2026, 6, 30), row.code
        else:
            assert row.effective_to is None, row.code
    # Before the first card nothing is guessed.
    assert (
        lookup(
            data_pk.ROWS, country="PK", kind="income_withholding", code="PK_153_1C_COMPANY_ATL", on=date(2025, 6, 30)
        )
        is None
    )


@pytest.mark.parametrize(("code", "ty2026", "ty2027"), EXPECTED)
def test_each_payee_class_and_atl_status_reads_its_card(code: str, ty2026: str, ty2027: str) -> None:
    for on, rate in ((TY2026, ty2026), (TY2027, ty2027)):
        row = lookup(data_pk.ROWS, country="PK", kind="income_withholding", code=code, on=on)
        assert row is not None, (code, on)
        assert row.rate_pct == D(rate), (code, on)


@pytest.mark.parametrize(("code", "ty2026", "ty2027"), EXPECTED)
def test_off_the_active_taxpayer_list_the_rate_doubles(code: str, ty2026: str, ty2027: str) -> None:
    if not code.endswith("_NON_ATL"):
        pytest.skip("checked from the non-ATL side")
    atl = next(item for item in EXPECTED if item[0] == code.replace("_NON_ATL", "_ATL"))
    assert D(ty2026) == 2 * D(atl[1])
    assert D(ty2027) == 2 * D(atl[2])


def test_independent_professionals_have_a_row_only_from_tax_year_2027() -> None:
    codes_2026 = {row.code for row in categories(data_pk.ROWS, country="PK", kind="income_withholding", on=TY2026)}
    codes_2027 = {row.code for row in categories(data_pk.ROWS, country="PK", kind="income_withholding", on=TY2027)}
    assert "PK_153_1B_PROFESSIONAL_ATL" not in codes_2026
    assert {"PK_153_1B_PROFESSIONAL_ATL", "PK_153_1B_PROFESSIONAL_NON_ATL"} <= codes_2027
    assert codes_2026 <= codes_2027


# ── The calculation ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("code", "withheld"),
    [
        # PKR 1,000,000 net plus 16% provincial sales tax: base PKR 1,160,000.
        ("PK_153_1C_COMPANY_ATL", "87000.00"),
        ("PK_153_1C_COMPANY_NON_ATL", "174000.00"),
        ("PK_153_1C_OTHER_ATL", "92800.00"),
        ("PK_153_1C_OTHER_NON_ATL", "185600.00"),
    ],
)
def test_a_works_contract_payment_withholds_by_payee_class_and_atl_status(code: str, withheld: str) -> None:
    figure = compute_payment_taxes(_inp(code, TY2027), rows_for("PK")).income_withheld
    assert figure.status == "value"
    assert figure.base == D("1160000.00")
    assert figure.amount == D(withheld)
    assert figure.review_status == "unconfirmed"


def test_services_rate_follows_the_tax_year_of_the_payment() -> None:
    before = compute_payment_taxes(_inp("PK_153_1B_OTHER_ATL", TY2026), rows_for("PK")).income_withheld
    after = compute_payment_taxes(_inp("PK_153_1B_OTHER_ATL", TY2027), rows_for("PK")).income_withheld
    assert (before.amount, after.amount) == (D("174000.00"), D("162400.00"))


def test_unknown_sales_tax_rate_holds_the_withholding_instead_of_guessing() -> None:
    figure = compute_payment_taxes(_inp("PK_153_1C_COMPANY_ATL", TY2027, vat=None), rows_for("PK")).income_withheld
    assert figure.status == "held"
    assert figure.amount is None


def test_a_payee_class_nobody_picked_is_held() -> None:
    inp = replace(_inp("PK_153_1C_COMPANY_ATL", TY2027), income_withholding=Choice("unset"))
    assert compute_payment_taxes(inp, rows_for("PK")).income_withheld.reason_key == "not_chosen"


# ── Where it shows: the payment certificate and the withholding scheme ───────


def test_a_pakistan_project_has_an_interim_payment_certificate() -> None:
    assert has_layout("PK")
    settings = resolve_settings("PK", None)
    by_tax = {line.tax_kind: line for line in settings.layout if line.op == "tax"}
    assert by_tax["income_withheld"].key == "income_tax_153"
    assert by_tax["income_withheld"].sign == -1
    assert by_tax["vat_computed"].key == "sales_tax"
    assert by_tax["vat_withheld"].key == "sales_tax_withholding"
    assert "stamp_duty" not in by_tax
    # The Turkish form reference is not printed under a Pakistani certificate.
    assert "PK" not in OFFICIAL_FORM_COUNTRIES
    assert DEFAULT_LAYOUTS["PK"] == settings.layout


def test_the_withholding_scheme_carries_the_tables_current_rates() -> None:
    regime = regime_by_scheme("PK_ITO_153_CONTRACTS")
    assert regime is not None
    assert regime["country_code"] == "PK" and regime["currency_code"] == "PKR"
    rates = {band["code"]: D(band["rate_pct"]) for band in regime["bands"]}
    assert rates == {
        "COMPANY_ATL": D("7.5"),
        "OTHER_ATL": D("8"),
        "COMPANY_NON_ATL": D("15"),
        "OTHER_NON_ATL": D("16"),
    }
    assert regime["default_band_code"] == "OTHER_NON_ATL"
    verified = {band["code"] for band in regime["bands"] if band["requires_verification"]}
    assert verified == {"COMPANY_ATL", "OTHER_ATL"}
