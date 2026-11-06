"""Demos installed at the same time share one guarantee credit line.

Onboarding provisions the chosen demos as parallel jobs, each on its own
session, and every demo of one currency draws its bonds on the same line
(``Ravi Guarantee Bank / PKR`` for the Pakistan demos). The line used to be a
plain read-then-insert, so two installs both missed it, both inserted, and the
loser failed its whole install on ``uq_guarantees_facility``: three of four
Pakistan demos failed when provisioned together.

The race is reproduced with two real connections: the first inserts the line
and holds its transaction open, the second asks for the line (its insert blocks
on the unique index), the first commits, and the second must come back with
the committed row instead of an IntegrityError.
"""

from __future__ import annotations

import asyncio
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.guarantees.demo import _facility
from app.modules.guarantees.models import GuaranteeFacility

pytestmark = pytest.mark.asyncio


async def test_a_second_install_reuses_the_line_the_first_one_committed(pg_engine) -> None:
    factory = async_sessionmaker(bind=pg_engine, class_=AsyncSession, expire_on_commit=False)
    bank = f"Race Test Bank {uuid.uuid4().hex[:8]}"
    try:
        async with factory() as first, factory() as second:
            mine = await _facility(first, bank, "PKR", Decimal("1000.00"))

            racing = asyncio.create_task(_facility(second, bank, "PKR", Decimal("2000.00")))
            await asyncio.sleep(0.5)  # let the second insert reach the unique index and wait
            assert not racing.done()
            await first.commit()

            theirs = await asyncio.wait_for(racing, timeout=30)
            await second.commit()

        assert theirs.id == mine.id
        async with factory() as check:
            count = (
                await check.execute(
                    select(func.count()).select_from(GuaranteeFacility).where(GuaranteeFacility.bank_name == bank)
                )
            ).scalar_one()
        assert count == 1
    finally:
        async with factory() as cleanup:
            await cleanup.execute(delete(GuaranteeFacility).where(GuaranteeFacility.bank_name == bank))
            await cleanup.commit()


async def test_an_existing_line_is_returned_not_duplicated(pg_session) -> None:
    bank = f"Reuse Test Bank {uuid.uuid4().hex[:8]}"
    a = await _facility(pg_session, bank, "PKR", Decimal("1000.00"))
    b = await _facility(pg_session, bank, "PKR", Decimal("1000.00"))
    assert a.id == b.id
