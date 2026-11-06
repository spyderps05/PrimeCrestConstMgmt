"""A Pakistani demo's order list has no empty orders.

The generic demo seeders that run over every demo project used to add orders
to the Pakistani demos that named no vendor (the cash-flow forecast's order)
or carried neither vendor nor price (the plant register's default story of
transformers and switchgear, told on a road in Faisalabad). After both have
run, every order of the Faisalabad road demo names a vendor and has an amount.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.demo_projects import install_demo_project
from app.modules.costmodel.cashflow_forecast_demo import seed_cashflow_forecast_demo
from app.modules.i18n_foundation.seed import seed_i18n_data
from app.modules.plant_register.models import PlantItem
from app.modules.plant_register.seed import seed_plant_register_demo
from app.modules.procurement.models import PurchaseOrder
from app.modules.projects.models import Project
from tests._pg import isolated_engine


@pytest.mark.asyncio
async def test_faisalabad_road_orders_all_name_a_vendor_and_an_amount() -> None:
    async with isolated_engine() as engine:
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            await seed_i18n_data(session)
            await session.commit()
        async with factory() as session:
            await install_demo_project(session, "faisalabad-road")
            await session.commit()
        async with factory() as session:
            projects = (await session.execute(select(Project))).scalars().all()
            project = next(p for p in projects if (p.metadata_ or {}).get("demo_id") == "faisalabad-road")
            assert project.country_code == "PK"
            result = await seed_plant_register_demo(session, [project.id])
            await session.commit()
            assert {"project_id": str(project.id), "note": "no_story_for_country"} in result["notes"]
        async with factory() as session:
            assert await seed_cashflow_forecast_demo(session, project.id, dip=False)
            await session.commit()
        async with factory() as session:
            items = (await session.execute(select(PlantItem).where(PlantItem.project_id == project.id))).all()
            assert items == []
            orders = (
                (await session.execute(select(PurchaseOrder).where(PurchaseOrder.project_id == project.id)))
                .scalars()
                .all()
            )
            assert orders
            assert not [o.po_number for o in orders if o.po_number.startswith("PO-PL-")]
            for order in orders:
                assert order.vendor_contact_id, order.po_number
                assert Decimal(order.amount_total or "0") > 0, order.po_number
            forecast = next(o for o in orders if o.po_number.endswith("-PO1"))
            assert forecast.notes and forecast.notes.endswith("materials supply")
