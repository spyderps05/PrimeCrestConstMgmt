"""A project's value counts each piece of scope once.

The Projects page summed every bill of quantities on a project, so a demo
project carrying its estimate and the control budget seeded beside it showed
twice its contract value. ``value_bill_ids`` picks the bills that make up the
value; these cases pin the rule.
"""

from __future__ import annotations

from app.modules.projects.project_value import BillRef, value_bill_ids


def _ids(bills: list[BillRef], project: str = "p1") -> set[str]:
    return value_bill_ids(bills).get(project, set())


def test_control_budget_beside_the_estimate_is_not_counted_again() -> None:
    bills = [
        BillRef(id="estimate", project_id="p1"),
        BillRef(id="budget", project_id="p1", estimate_type="budget"),
    ]
    assert _ids(bills) == {"estimate"}


def test_a_project_whose_only_bill_is_its_budget_keeps_that_value() -> None:
    assert _ids([BillRef(id="budget", project_id="p1", estimate_type="Budget")]) == {"budget"}


def test_only_the_newest_revision_counts() -> None:
    bills = [
        BillRef(id="rev0", project_id="p1"),
        BillRef(id="rev1", project_id="p1", parent_estimate_id="rev0"),
        BillRef(id="rev2", project_id="p1", parent_estimate_id="rev1"),
    ]
    assert _ids(bills) == {"rev2"}


def test_scenarios_variants_and_variation_bills_are_alternatives() -> None:
    bills = [
        BillRef(id="estimate", project_id="p1"),
        BillRef(
            id="what-if", project_id="p1", parent_estimate_id="estimate", metadata={"scenario": {"type": "what_if"}}
        ),
        BillRef(id="branch", project_id="p1", parent_estimate_id="estimate", branch_of_id="estimate"),
        BillRef(id="vr-bill", project_id="p1", variation_request_id="vr-1"),
        BillRef(id="option", project_id="p1", estimate_type="design_option"),
        BillRef(id="rom", project_id="p1", estimate_type="order_of_magnitude"),
    ]
    # The scenario names the estimate as its parent, and that must not make
    # the estimate look superseded.
    assert _ids(bills) == {"estimate"}


def test_bills_for_separate_scope_are_summed() -> None:
    bills = [
        BillRef(id="block-a", project_id="p1", estimate_type="detailed"),
        BillRef(id="block-b", project_id="p1"),
    ]
    assert _ids(bills) == {"block-a", "block-b"}


def test_projects_are_decided_independently() -> None:
    bills = [
        BillRef(id="a-estimate", project_id="a"),
        BillRef(id="a-budget", project_id="a", estimate_type="budget"),
        BillRef(id="b-budget", project_id="b", estimate_type="budget"),
    ]
    chosen = value_bill_ids(bills)
    assert chosen == {"a": {"a-estimate"}, "b": {"b-budget"}}


def test_the_pakistan_demo_portfolio_counts_each_project_once() -> None:
    """The four Pakistan demos each seed an estimate and a control budget of the same scope."""
    direct = {
        "lahore-house": 29_296_150,
        "school-karachi": 164_779_340,
        "bhu-punjab": 50_695_500,
        "faisalabad-road": 273_443_000,
    }
    bills = []
    totals = {}
    for slug, value in direct.items():
        bills.append(BillRef(id=f"{slug}-bill", project_id=slug))
        bills.append(BillRef(id=f"{slug}-budget", project_id=slug, estimate_type="budget"))
        totals[f"{slug}-bill"] = value
        totals[f"{slug}-budget"] = value
    chosen = value_bill_ids(bills)
    portfolio = sum(totals[b] for ids in chosen.values() for b in ids)
    assert portfolio == sum(direct.values()) == 518_213_990
