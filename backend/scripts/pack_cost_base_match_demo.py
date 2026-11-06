"""Match lines of the lahore-house demo bill against the Pakistan pack's rate books.

No database: every ``cost_base/*.json`` of the pakistan-pk pack is read, and each
bill line is scored against every book item with the two scorers the app uses
(``cost_match.matcher.best_match``, which ranks cost-match runs, and the lexical
scorer of ``costs.matcher`` behind ``POST /costs/match/``). It shows hit quality
before the books are loaded into a live install.

Run from ``backend/``::

    PYTHONPATH=. .venv/Scripts/python.exe scripts/pack_cost_base_match_demo.py [--all] [--dir DIR]
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
DEMO = ROOT / "backend" / "app" / "core" / "demo_packs" / "lahore-house.py"

# Ten lines that a Punjab MRS book should price, chosen across trades.
DEFAULT_LINES = ["03.01", "03.02", "06.01", "06.03", "06.10", "06.11", "07.01", "07.03", "09.01", "10.05"]


def _bill_lines() -> list[tuple[str, str, str, float]]:
    spec = importlib.util.spec_from_file_location("lahore_house_demo", DEMO)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = []
    for _sec, _title, _cls, rows in mod.SECTIONS:
        for ordinal, desc, unit, _qty, rate, _c in rows:
            out.append((ordinal, desc, unit, rate))
    return out


def _book_items(book_dir: Path) -> list[SimpleNamespace]:
    from app.modules.costs.pack_cost_base import book_label

    items = []
    for path in sorted(book_dir.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
        src = doc["source"]
        label = book_label(src)
        for it in doc.get("items", []):
            if it.get("rate_pkr") is None or not it.get("description"):
                continue
            items.append(
                SimpleNamespace(
                    id=uuid.uuid4(),
                    code=f"{src['id']}/{it['code']}",
                    description=it["description"],
                    descriptions={"en": it["description"]},
                    unit=it.get("unit") or "",
                    rate=str(it["rate_pkr"]),
                    label=label,
                )
            )
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="every bill line, not the default ten")
    ap.add_argument("--dir", type=Path, default=BOOK_DIR, help="directory of rate book JSON files")
    args = ap.parse_args()

    # The scorers import the ORM models, whose module builds (never connects) an
    # engine and refuses a non-PostgreSQL URL. Nothing here touches a database.
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://demo:demo@127.0.0.1:1/demo")

    from app.modules.cost_match.matcher import Candidate, best_match
    from app.modules.costs.matcher import _Candidate, _score_lexical

    items = _book_items(args.dir)
    if not items:
        print(f"No rate books in {args.dir}")
        return 1
    print(f"{len(items)} book items from {sorted(p.name for p in args.dir.glob('*.json'))}\n")
    by_ref = {str(i.id): i for i in items}
    cands = [Candidate(ref=str(i.id), text=i.description, unit=i.unit, payload={}) for i in items]

    lines = _bill_lines()
    if not args.all:
        lines = [ln for ln in lines if ln[0] in DEFAULT_LINES]
    for ordinal, desc, unit, rate in lines:
        outcome = best_match(desc, cands, query_unit=unit, top_n=3)
        lex = _score_lexical([_Candidate(item=i) for i in items], query=desc, unit=unit, lang="en")
        lex.sort(key=lambda c: -c.lexical)
        print(f"[{ordinal}] {desc} ({unit}, bill {rate:,.0f} PKR)")
        if outcome.candidate is None:
            print(f"   cost-match : no match ({outcome.hint})")
        else:
            hit = by_ref[outcome.candidate.ref]
            print(
                f"   cost-match : {outcome.score.confidence:.2f} {outcome.score.band:<6} {hit.code} "
                f"{hit.unit} {float(hit.rate):,.0f} PKR | {hit.description[:90]} | {hit.label}"
            )
        top = lex[0]
        print(
            f"   /costs/match: {top.lexical:.2f}        {top.item.code} {top.item.unit} "
            f"{float(top.item.rate):,.0f} PKR | {top.item.description[:90]}"
        )
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
