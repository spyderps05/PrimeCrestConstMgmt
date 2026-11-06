"""​‌‍⁠​‌‍⁠​‌‍⁠​‌‍⁠Pakistan pack: data rows, rule set, units, calendar, contract regimes and the demo template."""

from __future__ import annotations

import asyncio
import importlib.util
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.core.calendar import is_working_day
from app.core.payment_taxes import data_pk
from app.core.payment_taxes.tables import rows_for, validate_rows
from app.core.validation import rules as rules_pkg
from app.core.validation.engine import ValidationContext, rule_registry
from app.modules.boq.units import normalise_unit
from app.modules.contracts.country_defaults import (
    COUNTRY_CONTRACT_DEFAULTS,
    PAKISTAN_CONTRACT_FORMS,
    pakistan_contract_form,
)
from app.modules.contracts.price_adjustment import PRICE_ADJUSTMENT_REGIMES
from app.modules.contracts.public_procurement import PUBLIC_WORKS_LIMITS, PUBLIC_WORKS_PRICE_ADJUSTMENT, limit_value
from app.modules.payment_clock.data import PAYMENT_REGIMES

_ROOT = Path(__file__).resolve().parents[3]


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"_pk_{path.stem}".replace("-", "_"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pk_rows_are_unconfirmed_cited_and_valid() -> None:
    assert len(data_pk.ROWS) == 4
    for row in data_pk.ROWS:
        assert row.review_status == "unconfirmed"
        assert row.legal_reference
        assert row.source_url.startswith("https://")
        assert set(row.labels) == {"en", "ur"}
    assert validate_rows(rows_for("PK")) == []
    assert {r.rate_pct for r in data_pk.ROWS} == {Decimal("7.5"), Decimal("15"), Decimal("8"), Decimal("16")}


def test_non_atl_payee_pays_twice_the_rate() -> None:
    by_code = {r.code: r.rate_pct for r in data_pk.ROWS}
    assert by_code["PK_153_1C_COMPANY_NON_ATL"] == 2 * by_code["PK_153_1C_COMPANY_ATL"]
    assert by_code["PK_153_1C_OTHER_NON_ATL"] == 2 * by_code["PK_153_1C_OTHER_ATL"]


def test_contract_defaults_row_pk() -> None:
    row = COUNTRY_CONTRACT_DEFAULTS["PK"]
    assert row["retention_percent"]["value"] == "10"
    assert row["retention_cap_percent"]["value"] == "5"
    assert row["payment_period_days"]["value"] == 28
    assert row["retention_release_split"]["value"] is None


def test_public_works_figures_are_shown_never_enforced() -> None:
    limits = PUBLIC_WORKS_LIMITS["PK"]
    assert all(fig["needs_expert_review"] for key, fig in limits.items() if isinstance(fig, dict) and "value" in fig)
    assert limits["retention_percent"]["value"] == "10"
    assert limit_value(limits, "retention_percent") is None


def test_payment_clock_and_price_adjustment_regimes_registered() -> None:
    clock = next(r for r in PAYMENT_REGIMES if r["code"] == "pk_pec_sbd_clause_60")
    assert clock["country_code"] == "PK"
    assert clock["final_date_days"] == 28
    assert PUBLIC_WORKS_PRICE_ADJUSTMENT["PK"] in PRICE_ADJUSTMENT_REGIMES


def test_local_units() -> None:
    assert normalise_unit("sft") == "ft2"
    assert normalise_unit("cft") == "ft3"
    assert normalise_unit("rft") == "ft"
    assert normalise_unit("running ft") == "ft"
    assert normalise_unit("marla") == "marla"
    assert normalise_unit("Kanals") == "kanal"


def test_calendar_working_week_and_holidays() -> None:
    assert is_working_day(date(2026, 10, 23), "PK")  # Friday
    assert not is_working_day(date(2026, 10, 24), "PK")  # Saturday
    assert not is_working_day(date(2026, 8, 14), "PK")  # Independence Day
    assert not is_working_day(date(2026, 3, 23), "PK")  # Pakistan Day, a Monday
    # The 2025 Eid al-Fitr holiday was moved a day later by the Cabinet Division.
    assert not is_working_day(date(2025, 4, 2), "PK")


def test_pakistan_rule_set() -> None:
    rules_pkg.register_builtin_rules()
    found = rule_registry.get_rules_for_sets(["pakistan"])
    assert {r.rule_id for r in found} == {
        "pakistan.item_classified",
        "pakistan.sales_tax_line_present",
        "pakistan.sales_tax_rate_known",
    }
    good = [{"name": "Contractor's overhead", "percentage": "5"}, {"name": "Punjab sales tax", "percentage": "16"}]
    bad = [{"name": "Sales tax", "percentage": "61"}]
    no_tax = [{"name": "Contractor's overhead", "percentage": "5"}]

    def run(markups: list[dict]) -> list[bool]:
        ctx = ValidationContext(data={"positions": [], "markups": markups}, metadata={"locale": "en"})
        return [x.passed for r in found for x in asyncio.run(r.validate(ctx))]

    assert all(run(good))
    assert not all(run(bad))
    assert not all(run(no_tax))
    assert run([]) == []

    def classified(code: dict) -> list[bool]:
        pos = {"id": "1", "ordinal": "1", "classification": code}
        ctx = ValidationContext(data={"positions": [pos]}, metadata={"locale": "en"})
        return [x.passed for r in found for x in asyncio.run(r.validate(ctx))]

    assert classified({"masterformat": "03 30 00"}) == [True]
    assert classified({}) == [False]


def _direct_cost(template) -> int:
    total = 0.0
    for section in template.sections:
        for item in section[3]:
            total += float(item[3]) * float(item[4])
    return int(round(total))


def test_demo_jobs_offer_the_form_that_fits_the_price() -> None:
    bhu = _load(_ROOT / "backend/app/core/demo_packs/bhu-punjab.py").TEMPLATE
    house = _load(_ROOT / "backend/app/core/demo_packs/lahore-house.py").TEMPLATE
    road = _load(_ROOT / "backend/app/core/demo_packs/faisalabad-road.py").TEMPLATE
    assert bhu.project_metadata["contract_form"] == "pec_civil_works"
    assert house.project_metadata["marla_sqft"] == 225
    assert house.project_metadata["plot_marla"] == 10
    assert house.currency == "PKR" and house.locale == "en"
    assert road.project_metadata["contract_form"] == pakistan_contract_form(road.project_metadata["contract_price_pkr"])
    assert road.project_metadata["contract_form"] == "pec_sbd_2023_12"
    assert road.claim_retention == 0.10
    assert _direct_cost(road) == road.project_metadata["contract_price_pkr"]
    assert _direct_cost(road) > 100_000_000
    assert _direct_cost(bhu) == bhu.project_metadata["contract_price_pkr"]
    assert _direct_cost(house) == house.project_metadata["contract_price_pkr"]
    school = _load(_ROOT / "backend/app/core/demo_packs/school-karachi.py").TEMPLATE
    assert school.project_metadata["contract_form"] == "pec_sbd_2023_12"
    assert school.project_metadata["kanal_marlas"] == 20
    assert school.claim_retention == 0.10
    assert _direct_cost(school) == school.project_metadata["contract_price_pkr"]
    assert _direct_cost(school) > 100_000_000


def test_both_pec_forms_stay_separate() -> None:
    older = PAKISTAN_CONTRACT_FORMS["pec_civil_works"]
    large = PAKISTAN_CONTRACT_FORMS["pec_sbd_2023_12"]
    assert older["retention_percent_of_each_certificate"] == "10"
    assert older["retention_cap_percent_of_contract_price"] == "5"
    assert older["payment_period_days"] == 28
    assert large["performance_security_percent_of_accepted_contract_amount"] == "10"
    assert large["retention_money_limit_percent_of_contract_price"] == "5"
    assert "certificate" not in large
    assert pakistan_contract_form(25_000_000) == "pec_civil_works"
    assert pakistan_contract_form(100_000_000) == "pec_civil_works"
    assert pakistan_contract_form(100_000_001) == "pec_sbd_2023_12"


@pytest.mark.parametrize(
    ("demo_id", "tax_rate"),
    [("bhu-punjab", 16.0), ("school-karachi", 15.0), ("lahore-house", 16.0), ("faisalabad-road", 16.0)],
)
def test_demo_template_follows_the_pakistan_stack(demo_id: str, tax_rate: float) -> None:
    tpl = _load(_ROOT / "backend/app/core/demo_packs" / f"{demo_id}.py").TEMPLATE
    assert tpl.currency == "PKR"
    assert tpl.region == "PK"
    assert "pakistan" in tpl.validation_rule_sets
    tax = [m for m in tpl.markups if m[2] == "tax"]
    assert len(tax) == 1 and tax[0][1] == tax_rate
    assert tpl.claim_retention == 0.10
    assert tpl.progress_claims



@pytest.mark.parametrize("demo_id", ["bhu-punjab", "school-karachi", "lahore-house", "faisalabad-road"])
def test_the_demo_client_is_the_client_in_the_contacts(demo_id: str) -> None:
    """The project metadata and the client contact name the same employer, so no screen contradicts another."""
    from app.core.demo_packs._pakistan_demo_data import module_data_for

    tpl = _load(_ROOT / "backend/app/core/demo_packs" / f"{demo_id}.py").TEMPLATE
    clients = [c for c in module_data_for(demo_id)["contacts"] if c.get("contact_type") == "client"]
    assert clients, demo_id
    # A private client is addressed with an honorific in the metadata ("Mr. Kashif Mehmood").
    named = tpl.project_metadata["client"].removeprefix("Mr. ").removeprefix("Mrs. ")
    assert named in {c["company_name"] for c in clients}


def test_pack_manifest() -> None:
    import sys

    sys.path.insert(0, str(_ROOT / "packs/pakistan-pk/src"))
    try:
        from openconstructionerp_pakistan_pk import MANIFEST
    finally:
        sys.path.pop(0)
    assert MANIFEST.slug == "pakistan-pk"
    assert MANIFEST.default_currency == "PKR"
    assert MANIFEST.default_methodology == "pakistan"
    assert "pakistan" in MANIFEST.validation_rule_sets
    assert MANIFEST.hidden_modules == []
    assert "oe_boq" in MANIFEST.default_modules
    assert "oe_contracts" in MANIFEST.default_modules
    assert MANIFEST.metadata["support_name"] == "Spyder Solutions"
    assert "lahore-house" in MANIFEST.demo_template_ids
    assert "faisalabad-road" in MANIFEST.demo_template_ids
