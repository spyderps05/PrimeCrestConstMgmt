"""The rupee demo projects get a pinned FX policy, and the boot enrichment runs the seeder.

``seed_fx_demo`` was written but never wired into ``enrich_projects``, so no demo
install ever had a policy. These tests pin both halves: the seeder writes one
pinned PKR policy per rupee demo project (and nothing for a euro or a customer
project, nothing again on a re-run), and the enrichment's seeder list names it.
"""

from __future__ import annotations

import ast
import inspect
import uuid

import pytest
from sqlalchemy import func, select

from app.core import demo_enrichment
from app.modules.fx.models import RATE_MODE_PINNED, FxPolicy, FxRateSet
from app.modules.fx.seed import BASE_CURRENCY, BASE_DATE, seed_fx_demo
from app.modules.projects.models import Project
from app.modules.users.models import User


async def _project(session, name: str, *, currency: str, demo: bool) -> uuid.UUID:
    owner_id = uuid.uuid4()
    session.add(
        User(
            id=owner_id,
            email=f"fx-{name.lower()}-{owner_id.hex[:6]}@example.test",
            hashed_password="x",
            full_name=f"{name} Owner",
            role="admin",
            locale="en",
            is_active=True,
            metadata_={},
        )
    )
    await session.flush()
    project_id = uuid.uuid4()
    session.add(
        Project(
            id=project_id,
            name=name,
            description="FX seed fixture",
            currency=currency,
            status="active",
            owner_id=owner_id,
            metadata_={"demo_id": f"fixture-{name.lower()}"} if demo else {},
        )
    )
    await session.flush()
    return project_id


@pytest.mark.asyncio
async def test_rupee_demo_projects_get_a_pinned_policy_once(pg_session) -> None:
    rupee = await _project(pg_session, "Lahore", currency="PKR", demo=True)
    euro = await _project(pg_session, "Berlin", currency="EUR", demo=True)
    customer = await _project(pg_session, "Customer", currency="PKR", demo=False)

    first = await seed_fx_demo(pg_session, [rupee, euro, customer])
    await pg_session.flush()
    assert first["projects"] == 1, first

    policies = (await pg_session.execute(select(FxPolicy))).scalars().all()
    by_project = {p.project_id: p for p in policies}
    assert rupee in by_project
    assert euro not in by_project, "a euro project was pinned to the rupee rate set"
    assert customer not in by_project, "a customer project got a demo policy"
    policy = by_project[rupee]
    assert policy.rate_mode == RATE_MODE_PINNED
    assert policy.estimating_currency == BASE_CURRENCY
    rate_set = await pg_session.get(FxRateSet, policy.pinned_rate_set_id)
    assert rate_set is not None and rate_set.rate_date == BASE_DATE

    second = await seed_fx_demo(pg_session, [rupee, euro, customer])
    await pg_session.flush()
    assert second == {"projects": 0, "rate_sets": 0}, second
    count = (
        await pg_session.execute(select(func.count()).select_from(FxPolicy).where(FxPolicy.project_id == rupee))
    ).scalar_one()
    assert count == 1


def test_the_enrichment_runs_the_fx_seeder_on_the_demo_projects() -> None:
    """``seed_fx_demo`` is in the module-seeder list and handed the demo projects only."""
    tree = ast.parse(inspect.getsource(demo_enrichment.enrich_projects))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "seed_fx_demo"
    ]
    assert len(calls) == 1, "seed_fx_demo is not wired into enrich_projects"
    args = [ast.unparse(a) for a in calls[0].args]
    assert args == ["s", "_demo_pids"], args
