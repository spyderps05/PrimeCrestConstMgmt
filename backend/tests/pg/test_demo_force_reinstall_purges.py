"""``POST /api/demo/install/{id}?force=true`` replaces a demo that has a running approval on it.

The force path deleted the old project with ``session.delete``. A running approval instance carries no
project column, only a RESTRICT link to its project's route, so the route cascade failed with a foreign-key
error on ``oe_approval_routes_instance`` and the endpoint answered 500. It now goes through the same purge
as the uninstall endpoint.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select

from app.core.demo_projects import install_demo_project
from app.modules.approval_routes.models import Instance, Route
from app.modules.projects.models import Project

pytestmark = pytest.mark.asyncio

_DEMO_ID = "faisalabad-road"


async def _demo_projects(session) -> list[Project]:
    rows = (await session.execute(select(Project))).scalars().all()
    return [p for p in rows if isinstance(p.metadata_, dict) and p.metadata_.get("demo_id") == _DEMO_ID]


async def test_force_reinstall_survives_a_running_approval(pg_session) -> None:
    first = await install_demo_project(pg_session, _DEMO_ID, force_reinstall=True)
    old_id = uuid.UUID(str(first["project_id"]))

    route = Route(project_id=old_id, name="Payment certificate", target_kind="payment_certificate", is_active=True)
    pg_session.add(route)
    await pg_session.flush()
    route_id = route.id
    pg_session.add(
        Instance(
            route_id=route_id,
            target_kind="payment_certificate",
            target_id=uuid.uuid4(),
            started_at=datetime.now(UTC),
        )
    )
    await pg_session.flush()

    second = await install_demo_project(pg_session, _DEMO_ID, force_reinstall=True)
    new_id = uuid.UUID(str(second["project_id"]))
    await pg_session.flush()

    assert new_id != old_id
    assert [p.id for p in await _demo_projects(pg_session)] == [new_id]
    left = (
        await pg_session.execute(select(func.count()).select_from(Instance).where(Instance.route_id == route_id))
    ).scalar_one()
    assert left == 0, "the old project's approval instance survived the reinstall"
