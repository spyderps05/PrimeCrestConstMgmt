# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""Demo FX policy for the rupee projects of the demo estate.

A Pakistani project is estimated, bought and reported in rupees, but the lifts,
switchgear, solar inverters, LED fittings and a share of the steel are priced
abroad in dollars, euros or yuan. Under the PEC standard bidding documents the
rates of exchange the contract is held to are the ones that prevailed 28 days
before the bid deadline, so a project pins one locked rate set at that base date
and measures every later movement against it.

This seeder gives each demo project whose currency is PKR exactly that: one
locked, hand-entered rate set based on PKR (shared by the projects, keyed by its
base date) and a pinned policy that estimates, procures and reports in PKR.
The rates are indicative reference figures for the walkthrough, not State Bank
of Pakistan quotations.

Idempotent: a project that already has a policy is left alone, and the rate set
is reused when it exists. Only projects carrying the demo marker are touched.
The caller commits.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

#: Base date of the demo contracts: 28 days before the bid deadline of a project that starts on 1 April 2026.
BASE_DATE = date(2026, 3, 4)
BASE_CURRENCY = "PKR"
#: Rupees per one unit of the foreign currency at the base date (indicative, for the walkthrough).
PKR_PER_UNIT: dict[str, Decimal] = {
    "USD": Decimal("280.00"),
    "EUR": Decimal("302.40"),
    "CNY": Decimal("38.77"),
    "GBP": Decimal("357.90"),
    "AED": Decimal("76.24"),
}
SOURCE_REF = "Contract base date: rates prevailing 28 days before the bid deadline (PEC standard bidding documents)"
NOTE = (
    "Indicative reference rates for the demo projects, rupees per unit: USD 280.00, EUR 302.40, CNY 38.77, "
    "GBP 357.90, AED 76.24. Not State Bank of Pakistan quotations."
)
POLICY_NOTE = (
    "Estimate, commitments and reports in PKR. Imported items (lifts, switchgear, solar, LED fittings, part of the "
    "steel) are priced in USD, EUR or CNY and converted at the contract base-date rates; movements after the base "
    "date are measured against this pinned set."
)
_Q = Decimal("0.0000000001")


def _units_per_rupee() -> dict[str, Decimal]:
    """The register stores units of each currency per one unit of the base (one rupee)."""
    return {code: (Decimal(1) / per_unit).quantize(_Q) for code, per_unit in PKR_PER_UNIT.items()}


async def _rate_set_id(session: AsyncSession) -> uuid.UUID:
    """The demo base-date set: found when it exists, created and locked when it does not."""
    from app.modules.fx import repository as repo
    from app.modules.fx.models import SOURCE_MANUAL, FxRateSet

    found = (
        await session.execute(
            select(FxRateSet.id).where(
                FxRateSet.base_currency == BASE_CURRENCY,
                FxRateSet.rate_date == BASE_DATE,
                FxRateSet.source == SOURCE_MANUAL,
            )
        )
    ).scalar_one_or_none()
    if found is not None:
        return found
    rate_set = await repo.upsert_rate_set(
        session,
        base_currency=BASE_CURRENCY,
        rate_date=BASE_DATE,
        source=SOURCE_MANUAL,
        rates=_units_per_rupee(),
        source_ref=SOURCE_REF,
        note=NOTE,
        lock=True,
    )
    return rate_set.id


async def seed_fx_demo(session: AsyncSession, project_ids: Iterable[uuid.UUID]) -> dict[str, int]:
    """Give every rupee demo project in ``project_ids`` a pinned FX policy. The caller commits.

    Returns:
        ``{"projects": n, "rate_sets": m}``: policies written by this run, and 1 when the
        shared rate set was created by it.
    """
    from app.core.demo_marker import demo_id_of
    from app.modules.fx import repository as repo
    from app.modules.fx.models import RATE_MODE_PINNED, FxPolicy, FxRateSet
    from app.modules.projects.models import Project

    totals = {"projects": 0, "rate_sets": 0}
    ids = list(project_ids)
    if not ids:
        return totals
    rows = (
        await session.execute(select(Project.id, Project.currency, Project.metadata_).where(Project.id.in_(ids)))
    ).all()
    targets = [pid for pid, ccy, meta in rows if demo_id_of(meta) and (ccy or "").strip().upper() == BASE_CURRENCY]
    if not targets:
        return totals
    have = set((await session.execute(select(FxPolicy.project_id).where(FxPolicy.project_id.in_(targets)))).scalars())
    todo = [pid for pid in targets if pid not in have]
    if not todo:
        return totals

    existed = (
        await session.execute(
            select(FxRateSet.id).where(FxRateSet.base_currency == BASE_CURRENCY, FxRateSet.rate_date == BASE_DATE)
        )
    ).first() is not None
    try:
        async with session.begin_nested():
            set_id = await _rate_set_id(session)
    except Exception:
        logger.warning("fx demo seed: the base-date rate set could not be written, nothing seeded", exc_info=True)
        return totals
    totals["rate_sets"] = 0 if existed else 1

    for pid in todo:
        try:
            async with session.begin_nested():
                await repo.upsert_policy(
                    session,
                    pid,
                    estimating_currency=BASE_CURRENCY,
                    procurement_currency=BASE_CURRENCY,
                    reporting_currency=BASE_CURRENCY,
                    rate_mode=RATE_MODE_PINNED,
                    pinned_rate_set_id=set_id,
                    max_rate_age_days=30,
                    note=POLICY_NOTE,
                )
        except Exception:
            logger.warning("fx demo seed skipped for project=%s (non-fatal)", pid, exc_info=True)
            continue
        totals["projects"] += 1
    if totals["projects"]:
        logger.info("fx demo seed: %s", totals)
    return totals
