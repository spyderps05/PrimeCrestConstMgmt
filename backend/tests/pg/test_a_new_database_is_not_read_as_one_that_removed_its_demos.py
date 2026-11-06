"""A demo-backfill marker left by another database must not speak for a new one.

``demo_backfill_marker.json`` lives in the data dir, which survives a reinstall,
a new ``DATABASE_URL`` or a wiped embedded cluster. Read on its own, a marker
left by an earlier install made a brand-new, empty database look like one whose
demos had been deleted, so the first boot tombstoned every demo and the install
came up with none ("Recorded 6 demo(s) removed before this version").

The marker now counts only for the database it was stamped against: that
database carries a flag in ``oe_process_settings`` written next to the file. A
database from before the flag still has its marker honoured when it is evidently
not new (it holds a project or a demo-removal record).

The marker path also follows ``OE_DATA_DIR`` (the operator override every other
data-dir resolution honours), not only the CLI's ``OE_CLI_DATA_DIR``.
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import app.database as app_database
from app.modules.projects.models import Project
from app.modules.users.models import User

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def factory(pg_session, monkeypatch, tmp_path):
    """Session factory bound to this test's transaction, and an isolated data dir."""
    bound = async_sessionmaker(
        bind=pg_session.bind,
        class_=AsyncSession,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )
    monkeypatch.setattr(app_database, "async_session_factory", bound)
    for var in ("OE_CLI_DATA_DIR", "DATA_DIR"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("OE_DATA_DIR", str(tmp_path / "data"))
    return bound


async def _database_is_empty(factory) -> bool:
    async with factory() as s:
        return (await s.execute(select(Project.id).limit(1))).first() is None


async def test_the_marker_follows_oe_data_dir(factory, tmp_path: Path) -> None:
    import app.main as main

    assert main._demo_backfill_marker_path() == tmp_path / "data" / main._DEMO_BACKFILL_MARKER_FILENAME
    main._write_demo_backfill_version("9.9.9")
    assert (tmp_path / "data" / main._DEMO_BACKFILL_MARKER_FILENAME).is_file()
    assert main._read_demo_backfill_version() == "9.9.9"


async def test_a_stale_marker_does_not_speak_for_a_new_database(factory) -> None:
    import app.main as main

    if not await _database_is_empty(factory):
        pytest.skip("the shared test database already holds projects")
    # A marker an earlier install left in the same data dir.
    main._write_demo_backfill_version("9.9.9")
    assert main._read_demo_backfill_version() == "9.9.9"

    assert await main._demo_backfill_version_for_this_database() is None


async def test_the_marker_speaks_for_the_database_it_was_stamped_against(factory) -> None:
    import app.main as main

    if not await _database_is_empty(factory):
        pytest.skip("the shared test database already holds projects")
    main._write_demo_backfill_version("9.9.9")
    await main._mark_demo_backfill_in_database()

    assert await main._demo_backfill_version_for_this_database() == "9.9.9"


async def test_a_database_from_before_the_flag_keeps_its_marker(factory) -> None:
    """An upgraded install has a marker, no flag, and data: the marker still counts."""
    import app.main as main

    main._write_demo_backfill_version("9.9.9")
    async with factory() as s:
        owner_id = uuid.uuid4()
        s.add(
            User(
                id=owner_id,
                email=f"owner-{owner_id.hex[:8]}@example.test",
                hashed_password="x",
                full_name="Site Owner",
                role="admin",
                locale="en",
                is_active=True,
                metadata_={},
            )
        )
        await s.flush()
        s.add(
            Project(
                id=uuid.uuid4(),
                name="Existing work",
                description="",
                currency="PKR",
                status="active",
                owner_id=owner_id,
                metadata_={},
            )
        )
        await s.commit()

    assert await main._demo_backfill_version_for_this_database() == "9.9.9"


async def test_no_marker_means_no_version(factory) -> None:
    import app.main as main

    await main._mark_demo_backfill_in_database()
    assert await main._demo_backfill_version_for_this_database() is None
