"""Demo users seeded before the PrimeCrest rebrand move to the new addresses.

An existing database holds the three demo logins under the upstream
``@openconstructionerp.com`` addresses. Startup renames them in place, so the
seeder finds them under the new addresses instead of creating a second set.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.demo_accounts import (
    DEMO_ACCOUNT_EMAILS,
    LEGACY_DEMO_ACCOUNT_RENAMES,
    is_non_mailbox_login,
    rename_legacy_demo_accounts,
)
from tests._pg import transactional_session


def _user(email: str):
    from app.modules.users.models import User

    return User(
        id=uuid.uuid4(),
        email=email,
        hashed_password="x",
        full_name=email.split("@")[0],
        role="viewer",
        locale="en",
        is_active=True,
        metadata_={},
    )


def test_every_legacy_address_maps_to_a_current_demo_login() -> None:
    assert set(LEGACY_DEMO_ACCOUNT_RENAMES.values()) == set(DEMO_ACCOUNT_EMAILS)
    assert all(is_non_mailbox_login(old) for old in LEGACY_DEMO_ACCOUNT_RENAMES)


async def test_legacy_rows_are_renamed_and_the_rename_is_idempotent() -> None:
    from app.modules.users.models import User

    async with transactional_session() as s:
        ids = {}
        for old in LEGACY_DEMO_ACCOUNT_RENAMES:
            u = _user(old)
            ids[old] = u.id
            s.add(u)
        await s.flush()

        moved = await rename_legacy_demo_accounts(s)
        assert sorted(moved) == sorted(LEGACY_DEMO_ACCOUNT_RENAMES)
        for old, new in LEGACY_DEMO_ACCOUNT_RENAMES.items():
            row = (await s.execute(select(User).where(User.email == new))).scalar_one()
            assert row.id == ids[old]

        assert await rename_legacy_demo_accounts(s) == []


async def test_a_legacy_row_is_left_alone_when_the_new_address_exists() -> None:
    from app.modules.users.models import User

    old, new = next(iter(LEGACY_DEMO_ACCOUNT_RENAMES.items()))
    async with transactional_session() as s:
        s.add(_user(old))
        s.add(_user(new))
        await s.flush()

        assert old not in await rename_legacy_demo_accounts(s)
        emails = set((await s.execute(select(User.email).where(User.email.in_([old, new])))).scalars())
        assert emails == {old, new}
