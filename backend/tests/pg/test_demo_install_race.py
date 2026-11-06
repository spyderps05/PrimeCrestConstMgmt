"""The boot demo install and ``/partner-pack/full-install`` asking for the same demo must not race.

Both used to pass the duplicate check before either had committed, so the slower one died on a duplicate
key (or left a second copy), and both enrichment passes then raced each other's get-or-create of the
governance model (``uq_oe_gov_model_project``). An install now takes a per-demo advisory lock and the
enrichment runs one pass at a time, so the second caller waits and finds the first one's work.
"""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import demo_enrichment
from app.core.demo_projects import install_demo_project
from app.modules.projects.models import Project
from tests._pg import isolated_engine

_DEMO_ID = "faisalabad-road"


@pytest.mark.asyncio
async def test_two_concurrent_installs_of_one_demo_leave_one_project() -> None:
    async with isolated_engine() as engine:
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async def _install() -> dict:
            async with factory() as session:
                result = await install_demo_project(session, _DEMO_ID)
                await session.commit()
                return result

        first, second = await asyncio.gather(_install(), _install())

        assert first["project_id"] == second["project_id"], (first, second)
        assert [bool(r.get("already_installed")) for r in (first, second)].count(True) == 1
        async with factory() as session:
            rows = (await session.execute(select(Project.metadata_))).scalars().all()
        copies = [m for m in rows if isinstance(m, dict) and m.get("demo_id") == _DEMO_ID]
        assert len(copies) == 1, f"{len(copies)} copies of {_DEMO_ID} were installed"


@pytest.mark.asyncio
async def test_enrichment_passes_do_not_overlap() -> None:
    running = 0
    peak = 0

    @demo_enrichment._one_at_a_time
    async def _pass() -> None:
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        await asyncio.sleep(0.05)
        running -= 1

    await asyncio.gather(_pass(), _pass(), _pass())
    assert peak == 1


def test_the_enrichment_entry_point_is_serialised() -> None:
    assert getattr(demo_enrichment.enrich_projects, "__wrapped__", None) is not None


@pytest.mark.asyncio
async def test_two_different_demos_installed_at_once_on_a_fresh_database_both_land() -> None:
    """Both create the showcase owner on an empty database; the second must reuse it, not collide."""
    async with isolated_engine() as engine:
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async def _install(demo_id: str) -> dict:
            async with factory() as session:
                result = await install_demo_project(session, demo_id)
                await session.commit()
                return result

        results = await asyncio.gather(_install(_DEMO_ID), _install("lahore-house"))
        assert all(r.get("project_id") for r in results), results
