"""Rate books shipped inside a country pack, loaded into the shared cost base.

A country pack may carry its national or provincial schedules of rates as JSON
files, one file per book, under the directory its manifest names in
``metadata["cost_base_dir"]`` (the Pakistan pack: ``cost_base/punjab_mrs.json``,
``cost_base/mes_sr.json`` and so on). This module reads every ``*.json`` in that
directory and upserts its items into ``oe_costs_item`` so that the Costs page,
the lexical matcher (``POST /costs/match/``) and cost-match runs
(``/cost-match``) find them exactly like a CWICR base.

File format (see the pack's ``cost_base`` README in the brief)::

    {"source": {"id": "punjab_mrs", "name": "...", "publisher": "...",
                "edition": "2nd Biannual 2025", "effective_from": "2025-07-01",
                "region": "PK-PB", "district": "Lahore", "urls": [...],
                "retrieved": "2026-11-06", "notes": "..."},
     "items": [{"code": "MRS-03-12", "chapter": "Brickwork",
                "description": "...", "unit": "m3", "unit_as_printed": "%cft",
                "rate_pkr": 16850.0, "rate_as_printed": 47710.0,
                "kind": "item"}]}

How the rows are written:

* ``region`` is the pack's cost-base region (``metadata["cost_base_region"]``,
  falling back to ``metadata["country"]``), which is the ``region`` a project
  created under the pack carries ("PK"). Matching scoped to the project region
  therefore reaches the books with no extra mapping.
* ``source`` is :data:`RATE_BOOK_SOURCE` for every book; the book itself is
  named in ``classification`` (``collection`` = "Punjab MRS 2nd Biannual 2025,
  Lahore", ``department`` = chapter, ``rate_book`` = book id, ``book_code`` =
  the code as printed) and the full provenance sits in ``metadata``.
* ``code`` is ``"<book id>/<code as printed>"``: two provincial schedules number
  their items the same way, and ``(code, region)`` is unique.
* Re-import is keyed by ``(book id, code)``. Each row records a digest of the
  book file it came from; a book whose digest is unchanged is skipped, a new
  edition updates rows in place, inserts new codes and deactivates codes the new
  edition no longer prints (never deletes them: a BOQ line may still point at
  one).

Premium on a schedule of rates (MES, CSR tenders "x % above SR"): the platform
already models this as a BOQ markup with ``category="tender_adjustment"``
(positive above, negative below the schedule, on the bill or on one section;
validated by ``boq.markup.tender_adjustment_plausible``). The book rates are
loaded at par and the premium is applied there, so no per-item adjustment is
stored here.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from importlib import resources
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.costs.models import CostItem

logger = logging.getLogger(__name__)

#: ``CostItem.source`` of every row loaded from a pack rate book.
RATE_BOOK_SOURCE = "rate_book"

#: Manifest metadata keys this loader reads.
META_DIR_KEY = "cost_base_dir"
META_REGION_KEY = "cost_base_region"

_BOOK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]{0,39}$")
_DIR_RE = re.compile(r"^[A-Za-z0-9_\-]+(/[A-Za-z0-9_\-]+)*$")
_KINDS = {"item", "material", "labour", "plant"}
_MAX_CODE = 100
_MAX_UNIT = 20


@dataclass
class BookResult:
    """Outcome of loading one rate book file."""

    book_id: str
    file: str
    status: str  # inserted | updated | unchanged | error
    label: str = ""
    items: int = 0
    inserted: int = 0
    updated: int = 0
    deactivated: int = 0
    skipped: int = 0
    error: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v not in ("", None)}


@dataclass
class LoadResult:
    """Outcome of loading every rate book of one pack."""

    pack: str
    region: str
    books: list[BookResult] = field(default_factory=list)

    @property
    def items(self) -> int:
        return sum(b.items for b in self.books if b.status != "error")

    @property
    def changed(self) -> bool:
        return any(b.status in ("inserted", "updated") for b in self.books)

    def as_dict(self) -> dict[str, Any]:
        return {
            "pack": self.pack,
            "region": self.region,
            "items": self.items,
            "books": [b.as_dict() for b in self.books],
        }


# ── reading the files ───────────────────────────────────────────────────────


def book_label(source: dict[str, Any]) -> str:
    """Short human label: "Punjab MRS 2nd Biannual 2025, Lahore"."""
    name = str(source.get("short_name") or source.get("name") or source.get("id") or "").strip()
    # "Market Rate System (MRS)" reads better as its acronym plus the province.
    acronym = re.search(r"\(([A-Z][A-Za-z\-]{1,10})\)\s*$", name)
    region = str(source.get("region") or "").upper()
    province = {
        "PK-PB": "Punjab",
        "PK-SD": "Sindh",
        "PK-KP": "KP",
        "PK-BA": "Balochistan",
        "PK-IS": "Islamabad",
        "PK-GB": "Gilgit-Baltistan",
        "PK-JK": "AJK",
    }.get(region, "")
    if acronym and province and not source.get("short_name"):
        name = f"{province} {acronym.group(1)}".strip()
    edition = str(source.get("edition") or "").strip()
    # An edition that already names its book ("MES Schedule of Rates - 2014
    # (First Edition, August 2014)") is the whole label on its own.
    first_word = name.split()[0].lower() if name.split() else ""
    if first_word and edition.lower().startswith(first_word) and not source.get("short_name"):
        name = ""
    parts = [p for p in (name, edition) if p]
    label = " ".join(parts)
    district = str(source.get("district") or "").strip()
    if district:
        label = f"{label}, {district}"
    return label[:255]


def _pack_cost_base_files(slug: str, reldir: str) -> list[tuple[str, bytes]]:
    """Every ``*.json`` under ``reldir`` of the pack, as ``(name, bytes)``.

    Resolved the way :func:`app.core.partner_pack.discovery.read_pack_file`
    resolves a single file: an installed pack package first, then the source
    checkout under ``packs/``, then a pack dropped into the data directory.
    The first location that holds the directory wins.
    """
    from app.core.partner_pack import discovery

    if not _DIR_RE.match(reldir or ""):
        return []

    def _from_path(base: Path) -> list[tuple[str, bytes]] | None:
        root = (base / reldir).resolve()
        try:
            root.relative_to(base.resolve())
        except ValueError:
            return None
        if not root.is_dir():
            return None
        return [(p.name, p.read_bytes()) for p in sorted(root.glob("*.json")) if p.is_file()]

    mod_name = discovery._entrypoint_module_for_slug(slug)
    if mod_name:
        try:
            target = resources.files(mod_name).joinpath(reldir)
            if target.is_dir():
                found = sorted(
                    (entry.name, entry.read_bytes())
                    for entry in target.iterdir()
                    if entry.name.endswith(".json") and entry.is_file()
                )
                if found:
                    return found
        except (ModuleNotFoundError, FileNotFoundError, AttributeError, NotADirectoryError):
            pass

    for locate in (discovery._fs_package_dir_for_slug, discovery._data_dir_package_dir_for_slug):
        try:
            base = locate(slug)
        except Exception:  # noqa: BLE001 - a broken pack dir must not stop boot
            logger.debug("pack cost base: locating %s failed", slug, exc_info=True)
            continue
        if base is not None:
            found = _from_path(base)
            if found:
                return found
    return []


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not d.is_finite() or d < 0:
        return None
    return d


def _iso_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value)) if value else None
    except ValueError:
        return None


#: Bumped whenever the way a book becomes rows changes, so an unchanged file is
#: still re-imported once after an upgrade of this loader.
LOADER_VERSION = "2"


def _digest(raw: bytes) -> str:
    return hashlib.sha256(LOADER_VERSION.encode() + b"\0" + raw).hexdigest()[:16]


# ── description text for search ─────────────────────────────────────────────

# "Same as item 04-7, but CM 1:6": a schedule of rates prints a variant as a
# reference to its parent item. The reference alone tells neither a reader nor
# the matcher what the work is, so the parent's text is put in front of it.
_SAME_AS_RE = re.compile(r"^\s*same\s+as\s+(?:item\s+)?(?:no\.?\s*)?([0-9]+(?:[-./][0-9]+)+)\s*[,.;:]?\s*(.*)$", re.I)

# Abbreviations the Pakistani schedules print, spelled out in the matching text
# (``descriptions["en"]``). The ``description`` column keeps the book's wording.
_ABBREVIATIONS: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(pattern, re.I), repl)
    for pattern, repl in (
        (r"\bC\.?M\.?(?=\s*\d)", "cement sand mortar"),
        (r"\bP\.?C\.?C\b", "plain cement concrete"),
        (r"\bR\.?C\.?C\b", "reinforced cement concrete"),
        (r"\bC\.?C\b(?=\s*(?:type|\d|\())", "cement concrete"),
        (r"\bG\.?I\b", "galvanised iron"),
        (r"\bupto\b", "up to"),
        (r"\bincl\b\.?", "including"),
        (r"\bbrick\s+work\b", "brickwork brick masonry"),
        (r"\bG\.F\b", "ground floor"),
    )
)


def _code_key(code: str) -> str:
    """``"04-07"`` and ``"4-7"`` name the same item."""
    return "-".join(str(int(p)) if p.isdigit() else p for p in re.split(r"[-./]", code.strip()))


def _resolve_references(items: list[Any]) -> dict[int, str]:
    """``{index: resolved description}`` for items printed as "Same as item X, but ...".

    Resolved against the book's own items, one level deep per pass and at most
    three passes, so a chain of references reads in full while a cycle cannot
    loop. Unresolvable references are left as printed.
    """
    texts: dict[str, str] = {}
    for item in items:
        if isinstance(item, dict) and item.get("code") and item.get("description"):
            texts.setdefault(_code_key(str(item["code"])), " ".join(str(item["description"]).split()))
    out: dict[int, str] = {}
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        text = " ".join(str(item.get("description") or "").split())
        for _ in range(3):
            m = _SAME_AS_RE.match(text)
            if not m:
                break
            parent = texts.get(_code_key(m.group(1)))
            if not parent or parent == text:
                break
            text = f"{parent.rstrip('. ')}; {m.group(2)}".rstrip("; ")
        if text != " ".join(str(item.get("description") or "").split()):
            out[idx] = text
    return out


def _search_text(description: str) -> str:
    """The description with the book's abbreviations spelled out."""
    text = description
    for pattern, repl in _ABBREVIATIONS:
        text = pattern.sub(repl, text)
    return text


# ── writing the rows ────────────────────────────────────────────────────────


def _row_values(
    item: dict[str, Any],
    *,
    book_id: str,
    source: dict[str, Any],
    label: str,
    region: str,
    currency: str,
    digest: str,
    pack_slug: str,
    resolved: str | None = None,
) -> dict[str, Any] | None:
    """Column values for one book item, or ``None`` when it cannot be priced."""
    printed = str(item.get("code") or "").strip()
    as_printed = " ".join(str(item.get("description") or "").split())
    description = resolved or as_printed
    unit = str(item.get("unit") or "").strip()[:_MAX_UNIT]
    rate = _decimal(item.get("rate_pkr", item.get("rate")))
    if not printed or not description or not unit or rate is None:
        return None
    code = f"{book_id}/{printed}"[:_MAX_CODE]
    chapter = str(item.get("chapter") or "").strip()
    kind = str(item.get("kind") or "item").strip().lower()
    if kind not in _KINDS:
        kind = "item"
    classification = {
        "collection": label,
        "rate_book": book_id,
        "book_code": printed,
        "category": kind,
    }
    if chapter:
        classification["department"] = chapter
    metadata: dict[str, Any] = {
        "rate_book": {
            "id": book_id,
            "name": source.get("name"),
            "publisher": source.get("publisher"),
            "edition": source.get("edition"),
            "effective_from": source.get("effective_from"),
            "region": source.get("region"),
            "district": source.get("district"),
            "urls": list(source.get("urls") or []),
            "retrieved": source.get("retrieved"),
            "label": label,
        },
        "book_code": printed,
        "book_digest": digest,
        "pack": pack_slug,
        "unit_as_printed": item.get("unit_as_printed"),
        "rate_as_printed": item.get("rate_as_printed"),
        "kind": kind,
    }
    if description != as_printed:
        metadata["description_as_printed"] = as_printed
    return {
        "code": code,
        "description": description,
        "descriptions": {"en": _search_text(description)},
        "unit": unit,
        "rate": str(rate),
        "currency": currency,
        "source": RATE_BOOK_SOURCE,
        "classification": classification,
        "components": [],
        "tags": [RATE_BOOK_SOURCE, book_id],
        "region": region,
        "price_as_of": _iso_date(source.get("effective_from")),
        "catalog_id": None,
        "is_active": True,
        "metadata_": metadata,
    }


async def load_book(
    session: AsyncSession,
    raw: bytes,
    *,
    file_name: str,
    region: str,
    currency: str,
    pack_slug: str,
    force: bool = False,
) -> BookResult:
    """Upsert one rate book file. Does not commit."""
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return BookResult(book_id="", file=file_name, status="error", error=f"not valid JSON: {exc}")
    source = doc.get("source") if isinstance(doc, dict) else None
    items = doc.get("items") if isinstance(doc, dict) else None
    if not isinstance(source, dict) or not isinstance(items, list):
        return BookResult(book_id="", file=file_name, status="error", error="missing 'source' or 'items'")
    book_id = str(source.get("id") or Path(file_name).stem).strip().lower()
    if not _BOOK_ID_RE.match(book_id):
        return BookResult(book_id=book_id, file=file_name, status="error", error="invalid source.id")

    label = book_label(source)
    digest = _digest(raw)
    result = BookResult(book_id=book_id, file=file_name, status="unchanged", label=label)

    resolved = _resolve_references(items)
    rows: dict[str, dict[str, Any]] = {}
    for idx, item in enumerate(items):
        values = (
            _row_values(
                item,
                book_id=book_id,
                source=source,
                label=label,
                region=region,
                currency=currency,
                digest=digest,
                pack_slug=pack_slug,
                resolved=resolved.get(idx),
            )
            if isinstance(item, dict)
            else None
        )
        if values is None:
            result.skipped += 1
            continue
        rows[values["code"]] = values  # a duplicated code keeps its last printing
    result.items = len(rows)

    from app.core import cost_scope

    prefix = f"{book_id}/"
    scope = (CostItem.region == region, CostItem.code.startswith(prefix, autoescape=True))
    if not force:
        # Cheap probe first, so an unchanged book costs one aggregate per boot
        # rather than loading thousands of rows: same row count, every row
        # active and every row stamped with this file's digest.
        stamp = CostItem.metadata_["book_digest"].as_string()
        with cost_scope.system_scope():
            count, n_active, n_current = (
                await session.execute(
                    select(
                        func.count(),
                        func.count().filter(CostItem.is_active.is_(True)),
                        func.count().filter(stamp == digest),
                    ).where(*scope)
                )
            ).one()
        if count and count == n_active == n_current == len(rows):
            return result

    with cost_scope.system_scope():
        existing = (await session.execute(select(CostItem).where(*scope))).scalars().all()
    by_code = {row.code: row for row in existing}

    for code, values in rows.items():
        row = by_code.get(code)
        if row is None:
            session.add(CostItem(**values))
            result.inserted += 1
            continue
        for key, value in values.items():
            setattr(row, key, value)
        result.updated += 1
    for code, row in by_code.items():
        if code not in rows and row.is_active:
            row.is_active = False
            result.deactivated += 1
    await session.flush()
    result.status = "inserted" if not existing else "updated"
    return result


def pack_cost_base_settings(manifest: Any) -> tuple[str, str, str] | None:
    """``(dir, region, currency)`` the manifest declares, or ``None``."""
    meta = getattr(manifest, "metadata", None) or {}
    reldir = str(meta.get(META_DIR_KEY) or "").strip().strip("/")
    if not reldir:
        return None
    region = str(meta.get(META_REGION_KEY) or meta.get("country") or "").strip()
    if not region:
        return None
    currency = str(getattr(manifest, "default_currency", "") or "").strip().upper()
    return reldir, region, currency


async def load_pack_cost_base(
    session: AsyncSession,
    manifest: Any,
    *,
    force: bool = False,
) -> LoadResult | None:
    """Load every rate book a pack ships. Does not commit.

    Returns ``None`` when the pack declares no cost base. A book that fails is
    reported in its :class:`BookResult` and never stops the others.
    """
    settings = pack_cost_base_settings(manifest)
    if settings is None:
        return None
    reldir, region, currency = settings
    out = LoadResult(pack=manifest.slug, region=region)
    for name, raw in _pack_cost_base_files(manifest.slug, reldir):
        try:
            async with session.begin_nested():
                book = await load_book(
                    session,
                    raw,
                    file_name=name,
                    region=region,
                    currency=currency,
                    pack_slug=manifest.slug,
                    force=force,
                )
        except Exception as exc:  # noqa: BLE001 - one bad book must not stop the rest
            logger.warning("pack cost base %s/%s failed: %s", manifest.slug, name, exc)
            book = BookResult(book_id=Path(name).stem, file=name, status="error", error=str(exc))
        out.books.append(book)
    if out.changed:
        _invalidate_caches()
    return out


def _invalidate_caches() -> None:
    try:
        from app.modules.costs.router import _invalidate_cost_cache

        _invalidate_cost_cache()
    except Exception:  # noqa: BLE001 - cache refresh is best effort
        logger.debug("pack cost base: cost cache invalidation failed", exc_info=True)


async def load_active_pack_cost_base(*, force: bool = False) -> LoadResult | None:
    """Boot hook: load the active pack's rate books in their own session.

    Fail-soft by contract: any error is logged and ``None`` returned.
    """
    try:
        from app.core.partner_pack.discovery import get_active_pack
        from app.database import async_session_factory

        active = get_active_pack()
        if active is None or pack_cost_base_settings(active) is None:
            return None
        async with async_session_factory() as session:
            result = await load_pack_cost_base(session, active, force=force)
            await session.commit()
    except Exception:  # noqa: BLE001 - boot must not fail on a rate book
        logger.warning("Active pack cost base load skipped (non-fatal)", exc_info=True)
        return None
    if result is not None and result.books:
        logger.info(
            "Pack %s cost base: %s",
            result.pack,
            ", ".join(f"{b.book_id or b.file}={b.status}({b.items})" for b in result.books),
        )
    return result


__all__ = [
    "RATE_BOOK_SOURCE",
    "BookResult",
    "LoadResult",
    "book_label",
    "load_active_pack_cost_base",
    "load_book",
    "load_pack_cost_base",
    "pack_cost_base_settings",
]
