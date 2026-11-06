"""Ranking rules for rows from a country pack's schedules of rates.

Pure: no database, no app. Each rule is tested on its own helper and then
through both scorers that use it (cost-match ``best_match`` and the lexical
``costs.matcher._score_lexical``).
"""

from __future__ import annotations

import os
from decimal import Decimal
from types import SimpleNamespace

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://demo:demo@127.0.0.1:1/demo")

from app.modules.cost_match.matcher import Candidate, best_match, canonical_tokens, score_match  # noqa: E402
from app.modules.costs.rate_book_ranking import (  # noqa: E402
    RANK_NATIONAL,
    RANK_OTHER_PROVINCE,
    RANK_OWN_PROVINCE,
    UNIT_CONVERTIBLE,
    UNIT_INCOMPATIBLE,
    UNIT_SAME,
    book_rank,
    book_region,
    conversion_note,
    converted_rate,
    is_unwanted_variant,
    province_adjustment,
    province_for_project,
    province_from_text,
    unit_relation,
)


def _row(desc: str, unit: str, region: str | None, code: str = "x") -> SimpleNamespace:
    return SimpleNamespace(
        id=code,
        code=code,
        description=desc,
        descriptions={"en": desc},
        unit=unit,
        rate="100",
        source="rate_book" if region else "cwicr",
        metadata_={"rate_book": {"region": region}} if region else {},
    )


# ── a. province preference ────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("city", "expected"),
    [
        ("Lahore", "PK-PB"),
        ("Faisalabad", "PK-PB"),
        ("Karachi", "PK-SD"),
        ("Peshawar", "PK-KP"),
        ("Quetta", "PK-BA"),
        ("Islamabad", "PK-IS"),
        ("Berlin", None),
    ],
)
def test_province_from_city(city: str, expected: str | None) -> None:
    project = SimpleNamespace(subdivision_code=None, address={"city": city}, region="PK", metadata_={}, name="")
    assert province_for_project(project) == expected


def test_subdivision_code_wins_over_address_and_name() -> None:
    project = SimpleNamespace(
        subdivision_code="PK-KP", address={"city": "Lahore"}, region="PK", metadata_={}, name="Karachi school"
    )
    assert province_for_project(project) == "PK-KP"


def test_project_name_is_the_last_resort() -> None:
    project = SimpleNamespace(subdivision_code="", address=None, region="PK", metadata_={}, name="House, Lahore")
    assert province_for_project(project) == "PK-PB"
    assert province_from_text("pk-sd") == "PK-SD"
    assert province_from_text("Sindhi Traders") is None


def test_book_rank_orders_own_then_national_then_other() -> None:
    assert book_rank("PK-PB", "PK-PB") == RANK_OWN_PROVINCE
    assert book_rank("PK", "PK-PB") == RANK_NATIONAL
    assert book_rank("PK-KP", "PK-PB") == RANK_OTHER_PROVINCE
    # Sindh has no book: MES (national) is above every other province.
    assert province_adjustment("PK", "PK-SD") > province_adjustment("PK-PB", "PK-SD")
    # No province known: no preference at all.
    assert province_adjustment("PK-PB", None) == 0.0
    assert book_region(_row("a", "m3", None)) is None
    assert book_region(_row("a", "m3", "PK-pb")) == "PK-PB"


def _ranked(province: str | None) -> list[str]:
    text = "Plain cement concrete 1:4:8 in foundation"
    rows = [_row(text, "m3", region, code) for code, region in (("kp", "PK-KP"), ("mes", "PK"), ("pb", "PK-PB"))]
    cands = [
        Candidate(ref=r.code, text=r.description, unit=r.unit, preference=province_adjustment(book_region(r), province))
        for r in rows
    ]
    out = best_match(text, cands, query_unit="m3", top_n=3)
    return [c.ref for c, _ in out.alternatives]


def test_cost_match_ranks_the_project_province_book_first() -> None:
    assert _ranked("PK-PB") == ["pb", "mes", "kp"]
    assert _ranked("PK-KP") == ["kp", "mes", "pb"]
    # Karachi: no Sindh book, national MES first, the others still listed.
    assert _ranked("PK-SD") == ["mes", "kp", "pb"]


def test_province_preference_never_changes_the_confidence_shown() -> None:
    text = "Plain cement concrete 1:4:8 in foundation"
    cands = [Candidate(ref="kp", text=text, unit="m3", preference=-0.04)]
    out = best_match(text, cands, query_unit="m3")
    assert out.score is not None and out.score.confidence == 1.0


def test_lexical_scorer_ranks_the_project_province_book_first() -> None:
    from app.modules.costs.matcher import _Candidate, _score_lexical, rank_key

    text = "Plain cement concrete 1:4:8 in foundation"
    rows = [_row(text, "m3", region, code) for code, region in (("kp", "PK-KP"), ("mes", "PK"), ("pb", "PK-PB"))]
    scored = _score_lexical([_Candidate(item=r) for r in rows], query=text, unit="m3", lang=None, province="PK-PB")
    order = [c.item.code for c in sorted(scored, key=lambda c: rank_key(c.lexical, c))]
    assert order == ["pb", "mes", "kp"]
    # The score shown is the same for all three: only the order moved.
    assert len({c.lexical for c in scored}) == 1


# ── b. dismantling / repair variants ──────────────────────────────────────


@pytest.mark.parametrize(
    ("query", "candidate", "unwanted"),
    [
        ("Cement concrete 1:2:4", "Dismantling cement concrete plain 1:2:4", True),
        ("Cement concrete 1:2:4", "Removal of cement concrete", True),
        ("Cement concrete 1:2:4", "Demolition of cement concrete", True),
        ("Cement plaster 1:4", "Repair to cement plaster 1:4 in patches", True),
        ("Ceramic tiles", "Ceramic tiles as item 3-1, if fixed in repairs", True),
        ("Dismantling cement concrete", "Dismantling cement concrete plain 1:2:4", False),
        ("Repair of plaster", "Repair to cement plaster 1:4 in patches", False),
        # A new-work item that only mentions removal later is not a variant.
        ("Excavation in foundation", "Excavation in foundation of buildings including removal of surplus earth", False),
    ],
)
def test_unwanted_variant(query: str, candidate: str, unwanted: bool) -> None:
    assert is_unwanted_variant(query, candidate) is unwanted


def test_cost_match_penalises_a_variant_the_line_did_not_ask_for() -> None:
    query = "Plain cement concrete 1:2:4"
    new = "Plain cement concrete 1:2:4"
    old = "Dismantling plain cement concrete 1:2:4"
    s_new = score_match(query, new, query_unit="m3", candidate_unit="m3")
    s_old = score_match(query, old, query_unit="m3", candidate_unit="m3")
    assert "variant_unwanted" in s_old.reasons
    assert s_old.confidence < s_new.confidence
    out = best_match(
        query,
        [Candidate(ref="old", text=old, unit="m3"), Candidate(ref="new", text=new + " in foundation", unit="m3")],
        query_unit="m3",
    )
    assert out.candidate is not None and out.candidate.ref == "new"
    # Asked for: no penalty.
    asked = score_match("Dismantling plain cement concrete", old, query_unit="m3", candidate_unit="m3")
    assert "variant_unwanted" not in asked.reasons


def test_lexical_scorer_penalises_a_variant() -> None:
    from app.modules.costs.matcher import _Candidate, _score_lexical

    rows = [
        _row("Dismantling plain cement concrete 1:2:4", "m3", "PK-PB", "old"),
        _row("Plain cement concrete 1:2:4 in foundation", "m3", "PK-PB", "new"),
    ]
    scored = _score_lexical(
        [_Candidate(item=r) for r in rows], query="Plain cement concrete 1:2:4", unit="m3", lang=None
    )
    by = {c.item.code: c.lexical for c in scored}
    assert by["new"] > by["old"]


# ── c. units ──────────────────────────────────────────────────────────────


def test_unit_relations() -> None:
    assert unit_relation("m3", "m3") == UNIT_SAME
    assert unit_relation("t", "kg") == UNIT_CONVERTIBLE
    assert unit_relation("m3", "cft") == UNIT_CONVERTIBLE
    assert unit_relation("m2", "sft") == UNIT_CONVERTIBLE
    assert unit_relation("m3", "pcs") == UNIT_INCOMPATIBLE
    assert unit_relation("m2", "m3") == UNIT_INCOMPATIBLE
    assert conversion_note("t", "kg") == "1 t = 1000 kg"
    assert converted_rate(Decimal("250"), "t", "kg") == Decimal("250000")
    assert converted_rate("250", "m3", "pcs") is None


def test_cost_match_states_the_conversion_and_prefers_the_same_unit() -> None:
    s = score_match("Steel reinforcement bars", "Steel reinforcement bars", query_unit="t", candidate_unit="kg")
    assert "unit_converted" in s.reasons
    assert s.factors["unit_conversion"] == 1000.0
    out = best_match(
        "Steel reinforcement bars Grade 60",
        [
            Candidate(ref="pcs", text="Steel reinforcement bars Grade 60", unit="pcs"),
            Candidate(ref="kg", text="Steel reinforcement bars Grade 60 fixing", unit="kg"),
            Candidate(ref="t", text="Steel reinforcement bars Grade 60 fixing", unit="t"),
        ],
        query_unit="t",
        top_n=3,
    )
    assert [c.ref for c, _ in out.alternatives] == ["t", "kg", "pcs"]


def test_lexical_scorer_boosts_convertible_and_penalises_incompatible_units() -> None:
    from app.modules.costs.matcher import _Candidate, _score_lexical

    rows = [
        _row("Steel reinforcement bars Grade 60", "pcs", "PK-PB", "pcs"),
        _row("Steel reinforcement bars Grade 60", "kg", "PK-PB", "kg"),
        _row("Steel reinforcement bars Grade 60", "t", "PK-PB", "t"),
    ]
    scored = _score_lexical(
        [_Candidate(item=r) for r in rows], query="Steel reinforcement bars Grade 60", unit="t", lang=None
    )
    by = {c.item.code: c.lexical for c in scored}
    assert by["t"] >= by["kg"] > by["pcs"]


# ── d. shuttering / formwork / centering ──────────────────────────────────


def test_shuttering_formwork_and_centering_are_one_concept() -> None:
    assert canonical_tokens("shuttering") == canonical_tokens("formwork") == canonical_tokens("centering")
    s = score_match(
        "Formwork to slabs",
        "Centering and shuttering to slabs",
        query_unit="m2",
        candidate_unit="m2",
    )
    assert s.factors["query_coverage"] == 1.0
