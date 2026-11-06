"""Which bills of quantities make up a project's value.

A project can carry several bills, and most of them restate scope another bill
already prices: the demo seeder's control budget is the estimate again at
section level, a revision is a full copy of the bill it replaces, a what-if
scenario is a repriced copy, and a design-option or order-of-magnitude bill is
an alternative to the estimate rather than an addition to it. Summing every
bill on the project therefore counted the same work two or more times; the
Projects page showed each Pakistan demo at twice its contract value.

The rule here picks, per project, the bills that together are the project's
value:

1. Only bills of the project at large count: a bill raised for one variation
   request and an estimate branch (variant) are left out, the same filter the
   bill register uses.
2. A what-if scenario (``metadata.scenario``) is an alternative, not scope.
3. A bill that a later revision replaces (some other counted bill names it as
   ``parent_estimate_id``) is history, so only the newest revision counts.
4. Of what is left, control and alternative bills (``estimate_type`` budget,
   design option, order of magnitude, variation) give way to the priced
   estimate. They count only when the project has nothing else, so a project
   whose only bill is its budget still shows that budget's value.

Several bills can survive the rule, and then they are summed: two bills that
price different buildings of one project are both its scope.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

#: ``estimate_type`` values that describe a control figure or an alternative to
#: the estimate rather than the estimate itself.
NON_VALUE_ESTIMATE_TYPES: frozenset[str] = frozenset({"budget", "design_option", "order_of_magnitude", "variation"})


@dataclass(frozen=True)
class BillRef:
    """The columns of one bill the value rule reads."""

    id: str
    project_id: str
    estimate_type: str | None = None
    parent_estimate_id: str | None = None
    variation_request_id: str | None = None
    branch_of_id: str | None = None
    metadata: dict[str, Any] | None = None

    @property
    def is_scenario(self) -> bool:
        return isinstance(self.metadata, dict) and bool(self.metadata.get("scenario"))

    @property
    def is_control_or_alternative(self) -> bool:
        return (self.estimate_type or "").strip().lower() in NON_VALUE_ESTIMATE_TYPES


def value_bill_ids(bills: Iterable[BillRef]) -> dict[str, set[str]]:
    """Map each project id to the ids of the bills that make up its value."""
    by_project: dict[str, list[BillRef]] = defaultdict(list)
    for bill in bills:
        by_project[bill.project_id].append(bill)

    chosen: dict[str, set[str]] = {}
    for project_id, project_bills in by_project.items():
        register = [
            b for b in project_bills if b.variation_request_id is None and b.branch_of_id is None and not b.is_scenario
        ]
        superseded = {b.parent_estimate_id for b in register if b.parent_estimate_id}
        current = [b for b in register if b.id not in superseded]
        priced = [b for b in current if not b.is_control_or_alternative]
        chosen[project_id] = {b.id for b in (priced or current)}
    return chosen


def bill_ref_from_row(row: Any) -> BillRef:
    """Build a :class:`BillRef` from a row selecting the BOQ columns by name."""

    def _s(value: Any) -> str | None:
        return None if value is None else str(value)

    return BillRef(
        id=str(row.id),
        project_id=str(row.project_id),
        estimate_type=row.estimate_type,
        parent_estimate_id=_s(row.parent_estimate_id),
        variation_request_id=_s(row.variation_request_id),
        branch_of_id=_s(row.branch_of_id),
        metadata=row.metadata_ if isinstance(row.metadata_, dict) else None,
    )
