"""A MasterFormat bill is cut into its divisions, not swallowed by one all-zero line.

The demo seed cut the frame at depth 1. On a DIN 276 code (``331``) that is the cost group ``300``; on a
MasterFormat division (``01``, as the demo budget bill codes its section lines, or ``01 54 00``) it is
``00``/``000000``, the code of the whole classification, which covers every other division. The frame then
kept that one line with the general items under it, and the Faisalabad road (a Rs 273 million bill) showed a
frame of Rs 11.8 million. The seed now cuts at the first depth whose groups do not overlap.
"""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import select

from app.core.demo_projects import install_demo_project
from app.modules.economics.classification import overlaps
from app.modules.economics.models import FrameLine
from app.modules.economics.seed import frame_depth, seed_economics_demo

_PK = next((Path(__file__).resolve().parents[3] / "packs" / "pakistan-pk" / "src").glob("*/demo"))


def test_the_frame_depth_follows_the_shape_of_the_codes() -> None:
    assert frame_depth(["331", "341", "420"]) == 1  # DIN 276 cost groups
    assert frame_depth(["01 54 00", "31 23 16", "32 12 16", "03 30 00"]) == 2  # MasterFormat divisions
    assert frame_depth(["01", "26", "31", "32", "33"]) == 2  # MasterFormat divisions on a budget bill
    assert frame_depth(["2.6.1", "3.1"]) == 1  # NRM elements
    assert frame_depth([]) == 1


@pytest.mark.asyncio
async def test_the_faisalabad_road_frame_carries_the_whole_bill(pg_session, monkeypatch) -> None:
    story = json.loads((_PK / "faisalabad-road-economics.json").read_text(encoding="utf-8-sig"))
    monkeypatch.setattr("app.modules.project_governance.public.demo_module_story", lambda _d, _m: story)

    result = await install_demo_project(pg_session, "faisalabad-road", force_reinstall=True)
    pid = uuid.UUID(str(result["project_id"]))
    out = await seed_economics_demo(pg_session, [pid])
    await pg_session.flush()
    assert out["ok"] and out["projects"] == 1, out

    lines = (await pg_session.execute(select(FrameLine).where(FrameLine.project_id == pid))).scalars().all()
    codes = [line.code for line in lines]
    # The budget bill the plan reads carries one line per bill section, coded with its MasterFormat division.
    assert len(codes) >= 5, codes
    assert all(c.strip("0") for c in codes), f"a line covers the whole classification: {codes}"
    assert not any(overlaps(a, b) for i, a in enumerate(codes) for b in codes[i + 1 :]), codes
    framed = sum((line.amount for line in lines), Decimal(0))
    assert framed >= Decimal("273443000"), f"the frame carries Rs {framed} of a Rs 273 443 000 bill"
