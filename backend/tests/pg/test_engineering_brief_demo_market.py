"""The demo brief's baseline requirements and document language follow the project's market.

The seed used to put the same ten German requirements (Gebäude, DIN 18040, GEG 2024) and German study
reports in front of every story, so a Lahore house and a Faisalabad road both opened on a German brief.
A German demo still gets exactly that; a Pakistani building gets an English baseline on the Pakistani
codes, and a Pakistani road gets no building baseline at all.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.engineering_brief import seed as brief_seed
from app.modules.engineering_brief.permissions import register_engineering_brief_permissions
from app.modules.engineering_brief.service import EngineeringBriefService
from tests._pg import isolated_engine
from tests.pg.engineering_brief_fixtures import build_world

_PACKS = Path(__file__).resolve().parents[3] / "packs"
_PK = next((_PACKS / "pakistan-pk" / "src").glob("*/demo"))
_DE = next((_PACKS / "eleven-areas-framework" / "src").glob("*/demo"))

_GERMAN_MARKERS = ("Gebäude", "DIN 18040", "GEG 2024", "Brutto-Grundfläche", "Bauherr")


def _story(folder: Path, slug: str) -> dict:
    return json.loads((folder / f"{slug}-engineering_brief.json").read_text(encoding="utf-8-sig"))


def _project(**kw) -> SimpleNamespace:
    base = {"region": "", "country_code": None, "currency": "EUR", "project_type": None}
    return SimpleNamespace(**{**base, **kw})


# ── Pure choice of baseline and locale ──────────────────────────────────────


def test_a_german_project_keeps_the_german_baseline() -> None:
    story = _story(_DE, "school-ludwigsburg")
    assert brief_seed._market(_project(region="DE"), story) == ("de", "de")
    rows = brief_seed._requirement_rows("de", story)
    assert len(rows) == len(brief_seed._COMMON) + len(story["requirements"])


def test_a_pakistani_building_gets_the_pakistani_baseline_in_english() -> None:
    story = _story(_PK, "lahore-house")
    kind, locale = brief_seed._market(_project(region="PK", currency="PKR"), story)
    assert (kind, locale) == ("pk_building", "en")
    rows = brief_seed._requirement_rows(kind, story)
    text = " ".join(" ".join(r) for r in rows)
    assert not any(m in text for m in _GERMAN_MARKERS), text
    assert "PEC" in text and "NEECA" in text and "BCP-SP 2021" not in text  # the story's own seismic row wins
    seismic = [r for r in rows if (r[1], r[2]) == ("Structure", "Seismic design")]
    assert len(seismic) == 1 and seismic[0][4] == "Zone 2B"


def test_a_pakistani_road_gets_no_building_baseline() -> None:
    story = _story(_PK, "faisalabad-road")
    kind, locale = brief_seed._market(_project(region="PK", currency="PKR"), story)
    assert (kind, locale) == ("none", "en")
    rows = brief_seed._requirement_rows(kind, story)
    assert len(rows) == len(story["requirements"])
    assert not any(r[1] in {"Building", "Gebäude", "Accessibility"} for r in rows)


def test_a_story_can_pin_its_own_baseline_and_locale() -> None:
    story = {**_story(_PK, "school-karachi"), "baseline": "none", "locale": "ur"}
    assert brief_seed._market(_project(currency="PKR"), story) == ("none", "ur")


# ── Seeded through the service ──────────────────────────────────────────────


@pytest_asyncio.fixture
async def factory():
    register_engineering_brief_permissions()
    async with isolated_engine() as engine:
        yield async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.mark.asyncio
@pytest.mark.parametrize("slug", ["lahore-house", "faisalabad-road"])
async def test_a_pakistani_demo_brief_is_seeded_in_english(factory, slug: str) -> None:
    from app.modules.projects.models import Project

    w = await build_world(factory, governance=True, brief=False)
    story = _story(_PK, slug)
    async with w.factory() as s:
        project = await s.get(Project, w.project_id)
        project.region, project.currency, project.locale = "PK", "PKR", "en"
        await s.flush()
        counts = await brief_seed._seed_project(s, w.project_id, story)
        await s.commit()
    assert counts["studies"] == len(story["studies"]), counts
    async with w.factory() as s:
        views = await EngineeringBriefService(s).requirement_views(w.project_id)
    text = json.dumps(views, ensure_ascii=False)
    assert not any(m in text for m in _GERMAN_MARKERS), text
    if slug == "faisalabad-road":
        assert len(views) == len(story["requirements"])
    else:
        assert len(views) > len(story["requirements"])
