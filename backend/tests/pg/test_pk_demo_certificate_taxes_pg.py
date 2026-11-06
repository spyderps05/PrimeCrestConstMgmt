"""A Pakistani demo's payment certificates are seeded with their taxes worked out.

Installing the Lahore house demo stores, for each subcontractor payment
application, the section 153(1)(c) income tax (company on the Active Taxpayer
List, 7.5 %) and the Punjab sales tax on services (16 %), so the certificates
open with their deductions instead of every tax line held.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.demo_projects import install_demo_project
from app.modules.contracts import certificate_taxes
from app.modules.i18n_foundation.seed import seed_i18n_data
from app.modules.subcontractors.models import PaymentApplication, SubcontractAgreement
from app.modules.subcontractors.service import register_payment_application_as_tax_source
from app.modules.tax_withholding.service import register_certificate_tax_provider
from app.modules.tax_withholding.source_owners import unregister_source_owner
from tests._pg import isolated_engine


@pytest.mark.asyncio
async def test_lahore_demo_certificates_carry_wht_and_punjab_sales_tax() -> None:
    # What the modules register at startup: the tax module computes certificate
    # taxes, and a pay application is a document it may file them on.
    assert register_certificate_tax_provider()
    assert register_payment_application_as_tax_source()
    try:
        async with isolated_engine() as engine:
            factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with factory() as session:
                await seed_i18n_data(session)
                await session.commit()
            async with factory() as session:
                await install_demo_project(session, "lahore-house")
                await session.commit()
            async with factory() as session:
                agreements = (await session.execute(select(SubcontractAgreement))).scalars().all()
                agreement = next(a for a in agreements if (a.metadata_ or {}).get("demo_id") == "lahore-house")
                assert agreement.metadata_["hakedis"]["taxes"]["income_withholding"]["code"] == "PK_153_1C_COMPANY_ATL"
                apps = (
                    (
                        await session.execute(
                            select(PaymentApplication).where(PaymentApplication.agreement_id == agreement.id)
                        )
                    )
                    .scalars()
                    .all()
                )
                assert apps
                for app_row in apps:
                    state = await certificate_taxes.collect_certificate_tax_state(
                        session, "sub_payment_application", app_row.id
                    )
                    assert state is not None, app_row.application_number
                    income = state.result.income_withheld
                    assert income.status == "value", (app_row.application_number, income)
                    assert income.rate_pct == Decimal("7.5")
                    assert state.result.vat_computed.status == "value"
                    assert state.vat_rate_pct == Decimal("16")
                    # No stamp duty on a Pakistani certificate, and nothing waits on it.
                    assert state.choices["stamp_duty"].state == "not_applicable"
    finally:
        certificate_taxes.unregister_certificate_tax_provider()
        certificate_taxes.unregister_certificate_tax_writer()
        unregister_source_owner("sub_payment_application")
