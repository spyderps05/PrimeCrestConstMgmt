"""The Pakistani demo payment certificates open with their deductions decided.

What the demo seeds is data, so it is checked here against the code that will
read it: the subcontract's certificate configuration must resolve under the
PK layout, its income tax choice must be a section 153 row in force on the demo
dates, and each Pakistani demo project must say which province it is in, which
is what picks the provincial sales tax on services (PRA 16 %, SRB 15 %).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.core import demo_projects
from app.core.payment_taxes.tables import lookup, rows_for
from app.modules.contracts.hakedis_layout import choice_kinds_for_layout, resolve_settings


def test_pk_demo_subcontract_terms_resolve_under_the_pk_layout() -> None:
    settings = resolve_settings("PK", {"hakedis": demo_projects._PK_DEMO_HAKEDIS})
    income = settings.tax_choices["income_withholding"]
    assert income.state == "selected"
    assert income.code == "PK_153_1C_COMPANY_ATL"
    # Every tax the PK layout prints is decided, so no line waits on a person.
    for kind in choice_kinds_for_layout(settings.layout):
        assert settings.tax_choices[kind].state in ("selected", "not_applicable")
    assert "stamp_duty" not in choice_kinds_for_layout(settings.layout)


@pytest.mark.parametrize("on", [date(2026, 3, 31), date(2026, 9, 30)])
def test_the_income_tax_choice_is_the_company_atl_rate(on: date) -> None:
    row = lookup(rows_for("PK"), country="PK", kind="income_withholding", code="PK_153_1C_COMPANY_ATL", on=on)
    assert row is not None
    assert row.rate_pct == Decimal("7.5")
    assert "153(1)(c)" in row.legal_reference


@pytest.mark.parametrize(
    ("demo_id", "province"),
    [
        ("lahore-house", "PK-PB"),
        ("faisalabad-road", "PK-PB"),
        ("bhu-punjab", "PK-PB"),
        ("school-karachi", "PK-SD"),
    ],
)
def test_pakistani_demos_name_their_province(demo_id: str, province: str) -> None:
    import app.core.demo_packs  # noqa: F401, PLC0415 - registers the pack templates

    template = demo_projects.DEMO_TEMPLATES.get(demo_id)
    if template is None:
        pytest.skip(f"demo pack {demo_id} not registered in this build")
    assert template.subdivision_code == province
