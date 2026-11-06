# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""​‌‍⁠​‌‍⁠​‌‍⁠​‌‍⁠The seeded demo identities, named once.

These three addresses are logins, not mailboxes. They live on a domain we
own, and on that domain exactly one mailbox exists, so a message addressed
to any of them is refused by the receiving server and comes back as a hard
bounce against our own sending reputation. In September 2026 that is what
took outbound mail down for the whole account: a background sweeper nudged
the same permanently overdue demo items twice a day, every one of those
nudges bounced, and the host disabled sending.

The list already existed in three places, each with a comment saying the
others had to stay in sync with it. This module is the one they now import,
so "in sync" is a property of the code rather than a request to the reader.

``is_demo_account`` is deliberately the only way to ask the question:
comparing an address by hand skips the case folding and the strip, and an
address that differs from the list only in case is exactly the one that
would slip past a guard and bounce.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

#: Logins seeded for the public walkthrough. Never mailable, see the module
#: docstring. Mirrors the specs in ``app.main._seed_demo_account``.
DEMO_ACCOUNT_EMAILS: frozenset[str] = frozenset(
    {
        "demo@primecrest.pk",
        "estimator@primecrest.pk",
        "manager@primecrest.pk",
    }
)


#: Addresses the same three demo logins carried before the PrimeCrest
#: rebrand, mapped to the address each one has now. An existing database still
#: holds rows under the old addresses; :func:`rename_legacy_demo_accounts`
#: moves them across at startup so the seeder finds them instead of creating
#: a second set of demo users beside them.
LEGACY_DEMO_ACCOUNT_RENAMES: dict[str, str] = {
    "demo@openconstructionerp.com": "demo@primecrest.pk",
    "estimator@openconstructionerp.com": "estimator@primecrest.pk",
    "manager@openconstructionerp.com": "manager@primecrest.pk",
}


#: The account that owns the showcase projects. Seeders used to take the first
#: row with role ``admin``, which on a live installation is a real person, and
#: could be one whose account had been deactivated.
SHOWCASE_OWNER_EMAIL = "demo@primecrest.pk"


#: The account behind the "Admin" tile on the login page. When it is and is
#: not an administrator is decided in ``app.core.demo_admin``.
DEMO_ADMIN_EMAIL = "demo@primecrest.pk"


#: The ``ADMIN_EMAIL`` each seeder script under ``app/scripts`` registers.
#: They log in and, failing that, POST a registration, so any installation
#: that has run one of those scripts holds the account. None of them is a
#: mailbox: they were created as credentials and no inbox was ever made.
#:
#: ``demo@openestimator.io`` is not a typo of the other. It is a different
#: domain, seeded only by ``seed_demo_v2``, and it is the reason this list is
#: kept beside a test that reads the constants back out of the scripts rather
#: than being maintained by hand. A grep written from memory for our three
#: known domains does not match it, which is how it stayed unguarded.
SEEDED_ADMIN_EMAILS: frozenset[str] = frozenset(
    {
        "admin@openestimate.io",
        "demo@openestimator.io",
    }
)

#: Every address the product must refuse to send mail to.
#:
#: Deliberately NOT folded into ``DEMO_ACCOUNT_EMAILS`` above, because that
#: set is not only "these are not mailboxes". It is also the whitelist of the
#: passwordless ``/auth/demo-login`` endpoint and the list the demo reset
#: deletes, so putting an admin address in it would hand out a password-free
#: login to an administrator account. The two questions happen to have had the
#: same answer for three addresses; they are not the same question.
NON_MAILBOX_LOGINS: frozenset[str] = (
    DEMO_ACCOUNT_EMAILS | SEEDED_ADMIN_EMAILS | frozenset(LEGACY_DEMO_ACCOUNT_RENAMES)
)


#: Top-level names that can never hold a mailbox (RFC 2606, RFC 6761).
RESERVED_MAIL_TLDS: frozenset[str] = frozenset({"invalid", "test", "example", "localhost"})

#: Second-level names reserved for documentation (RFC 2606), any subdomain too.
RESERVED_MAIL_DOMAINS: frozenset[str] = frozenset({"example.com", "example.net", "example.org"})


def is_reserved_mail_domain(email: str | None) -> bool:
    """True when ``email`` sits on a domain that cannot receive mail.

    Fixtures, demo installs and placeholder form input use these names, and
    a message to one is a bounce or deferral on our relay account. Matching
    is by label, so ``example-contractor.com`` or ``test.de`` are not caught.
    """
    if not email or "@" not in email:
        return False
    domain = email.strip().rsplit("@", 1)[1].lower().rstrip(".")
    if not domain:
        return False
    if domain.rsplit(".", 1)[-1] in RESERVED_MAIL_TLDS:
        return True
    return any(domain == d or domain.endswith("." + d) for d in RESERVED_MAIL_DOMAINS)


def is_demo_account(email: str | None) -> bool:
    """True when ``email`` is one of the seeded demo logins.

    This is the authentication question: may this address use the demo
    login, and is it cleared by the demo reset. For "may we send mail to
    it", ask :func:`is_non_mailbox_login` instead - the sets differ.
    """
    if not email:
        return False
    return email.strip().lower() in DEMO_ACCOUNT_EMAILS


def is_non_mailbox_login(email: str | None) -> bool:
    """True when ``email`` is a seeded login rather than a real mailbox.

    Every address this returns True for bounces, because it was created by a
    seeder as a credential and no mailbox was ever made for it. This is the
    question the mail transport has to ask.
    """
    if not email:
        return False
    return email.strip().lower() in NON_MAILBOX_LOGINS


async def rename_legacy_demo_accounts(session: AsyncSession) -> list[str]:
    """Move demo users still on a pre-rebrand address to the current one.

    Idempotent: a row is renamed only when its old address exists and nothing
    holds the new one yet. When both exist (someone already seeded the new
    accounts beside the old ones) the old row is left alone rather than
    merged, since it may own data. Returns the old addresses that were moved.
    The caller commits.
    """
    from sqlalchemy import func, select

    from app.modules.users.models import User

    moved: list[str] = []
    for old, new in LEGACY_DEMO_ACCOUNT_RENAMES.items():
        legacy = (
            await session.execute(select(User).where(func.lower(User.email) == old))
        ).scalar_one_or_none()
        if legacy is None:
            continue
        current = (
            await session.execute(select(User.id).where(func.lower(User.email) == new))
        ).first()
        if current is not None:
            continue
        legacy.email = new
        moved.append(old)
    if moved:
        await session.flush()
    return moved
