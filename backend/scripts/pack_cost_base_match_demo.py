"""Match the lines of a Pakistan demo bill against the Pakistan pack's rate books.

No database: every ``cost_base/*.json`` of the pakistan-pk pack is read, and each
bill line is scored against every book item with the two scorers the app uses
(``cost_match.matcher.best_match``, which ranks cost-match runs, and the lexical
scorer of ``costs.matcher`` behind ``POST /costs/match/``). It shows hit quality
before the books are loaded into a live install.

The province of the demo project (from its address: Lahore and Faisalabad are
Punjab) is passed to both scorers, as a live run passes the project's, so rows
of that province's book rank first, the national MES schedule next.

At the end a summary counts, for the cost-match top hit:

* ``reviewable``: confidence at or above the review band (0.45);
* ``unit ok``: priced in the line's unit or one that converts to it;
* ``no variant``: not a dismantling/removal/repair row the line did not ask for;
* ``hit``: all three at once - the hit rate;
* ``own book``: taken from the project's province book (or MES where the
  province has none).

and the ``lex ...`` counts say the same of the ``/costs/match`` top row.

Run from ``backend/``::

    PYTHONPATH=. .venv/Scripts/python.exe scripts/pack_cost_base_match_demo.py [--all] [--demo faisalabad-road]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
BOOK_DIR = ROOT / "packs" / "pakistan-pk" / "src" / "openconstructionerp_pakistan_pk" / "cost_base"
DEMO_DIR = ROOT / "backend" / "app" / "core" / "demo_packs"

# Ten lines of the Lahore house that a Punjab MRS book should price, chosen across trades.
DEFAULT_LINES = ["03.01", "03.02", "06.01", "06.03", "06.10", "06.11", "07.01", "07.03", "09.01", "10.05"]


def _demo(name: str) -> object:
    spec = importlib.util.spec_from_file_location(f"demo_{name.replace('-', '_')}", DEMO_DIR / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _bill_lines(mod: object) -> list[tuple[str, str, str, float]]:
    out = []
    for _sec, _title, _cls, rows in mod.SECTIONS:  # type: ignore[attr-defined]
        for ordinal, desc, unit, _qty, rate, _c in rows:
            out.append((ordinal, desc, unit, rate))
    return out


def _book_items(book_dir: Path) -> list[SimpleNamespace]:
    from app.modules.costs.pack_cost_base import _resolve_references, _search_text, book_label

    items = []
    for path in sorted(book_dir.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
        src = doc["source"]
        label = book_label(src)
        resolved = _resolve_references(doc.get("items", []))
        for idx, it in enumerate(doc.get("items", [])):
            if it.get("rate_pkr") is None or not it.get("description"):
                continue
            # The same text the loader writes: references resolved, abbreviations spelled out.
            desc = resolved.get(idx) or " ".join(it["description"].split())
            items.append(
                SimpleNamespace(
                    id=uuid.uuid4(),
                    code=f"{src['id']}/{it['code']}",
                    description=desc,
                    descriptions={"en": _search_text(desc)},
                    unit=it.get("unit") or "",
                    rate=str(it["rate_pkr"]),
                    label=label,
                    source="rate_book",
                    metadata_={"rate_book": {"region": src.get("region")}},
                )
            )
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="every bill line, not the default ten")
    ap.add_argument("--demo", default="lahore-house", help="demo pack (lahore-house, faisalabad-road, ...)")
    ap.add_argument("--dir", type=Path, default=BOOK_DIR, help="directory of rate book JSON files")
    args = ap.parse_args()

    # The scorers import the ORM models, whose module builds (never connects) an
    # engine and refuses a non-PostgreSQL URL. Nothing here touches a database.
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://demo:demo@127.0.0.1:1/demo")

    from app.modules.cost_match.matcher import REVIEW_CONFIDENCE, Candidate, best_match
    from app.modules.costs.matcher import _Candidate, _score_lexical, rank_key
    from app.modules.costs.rate_book_ranking import (
        UNIT_CONVERTIBLE,
        UNIT_INCOMPATIBLE,
        book_rank,
        book_region,
        conversion_note,
        converted_rate,
        is_unwanted_variant,
        province_adjustment,
        province_for_project,
        unit_relation,
    )

    items = _book_items(args.dir)
    if not items:
        print(f"No rate books in {args.dir}")
        return 1
    mod = _demo(args.demo)
    template = mod.TEMPLATE  # type: ignore[attr-defined]
    project = SimpleNamespace(
        subdivision_code=getattr(template, "subdivision_code", ""),
        address=template.address,
        region=template.region,
        metadata_=template.project_metadata,
        name=template.project_name,
    )
    province = province_for_project(project)
    regions = {book_region(i) for i in items}
    own_region = province if province in regions else "PK"
    print(f"{len(items)} book items from {sorted(p.name for p in args.dir.glob('*.json'))}")
    print(f"Demo {args.demo}: province {province or 'unknown'}, preferred book region {own_region}\n")

    by_ref = {str(i.id): i for i in items}
    cands = [
        Candidate(
            ref=str(i.id),
            text=i.descriptions["en"],
            unit=i.unit,
            payload={},
            preference=province_adjustment(book_region(i), province),
        )
        for i in items
    ]

    lines = _bill_lines(mod)
    if not args.all and args.demo == "lahore-house":
        lines = [ln for ln in lines if ln[0] in DEFAULT_LINES]
    counts = dict.fromkeys(
        ("lines", "reviewable", "unit ok", "no variant", "hit", "own book", "lex own book", "lex unit ok", "lex no variant"),
        0,
    )
    for ordinal, desc, unit, rate in lines:
        outcome = best_match(desc, cands, query_unit=unit, top_n=3)
        lex = _score_lexical([_Candidate(item=i) for i in items], query=desc, unit=unit, lang="en", province=province)
        lex.sort(key=lambda c: rank_key(c.lexical, c))
        print(f"[{ordinal}] {desc} ({unit}, bill {rate:,.0f} PKR)")
        counts["lines"] += 1
        if outcome.candidate is None or outcome.score is None:
            print(f"   cost-match : no match ({outcome.hint})")
        else:
            hit = by_ref[outcome.candidate.ref]
            reviewable = outcome.score.confidence >= REVIEW_CONFIDENCE
            unit_ok = unit_relation(unit, hit.unit) != UNIT_INCOMPATIBLE
            no_variant = not is_unwanted_variant(desc, hit.description)
            own = book_rank(book_region(hit), own_region) == 0
            for key, flag in (("reviewable", reviewable), ("unit ok", unit_ok), ("no variant", no_variant), ("own book", own)):
                counts[key] += int(flag)
            counts["hit"] += int(reviewable and unit_ok and no_variant)
            per_line = ""
            if unit_relation(unit, hit.unit) == UNIT_CONVERTIBLE:
                conv = converted_rate(hit.rate, unit, hit.unit)
                per_line = f" [{conversion_note(unit, hit.unit)}: {float(conv or 0):,.0f} PKR/{unit}]"
            print(
                f"   cost-match : {outcome.score.confidence:.2f} {outcome.score.band:<6} {hit.code} "
                f"{hit.unit} {float(hit.rate):,.0f} PKR{per_line} | {hit.description[:90]} | {hit.label}"
            )
        top = lex[0]
        counts["lex own book"] += int(book_rank(book_region(top.item), own_region) == 0)
        counts["lex unit ok"] += int(unit_relation(unit, top.item.unit) != UNIT_INCOMPATIBLE)
        counts["lex no variant"] += int(not is_unwanted_variant(desc, top.item.description))
        print(
            f"   /costs/match: {top.lexical:.2f}        {top.item.code} {top.item.unit} "
            f"{float(top.item.rate):,.0f} PKR | {top.item.description[:90]}"
        )
        print()
    n = max(counts["lines"], 1)
    print("Summary (cost-match top hit): " + ", ".join(f"{k} {v}/{n} ({100 * v / n:.0f}%)" if k != "lines" else f"{v} lines" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
