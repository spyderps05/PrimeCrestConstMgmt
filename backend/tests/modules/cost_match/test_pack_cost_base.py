"""A country pack's rate books land in the cost base and are matched for its projects.

Loads the synthetic ``tests/fixtures/pack_cost_base/test_mrs.json`` through
:mod:`app.modules.costs.pack_cost_base` into a region no other suite uses, then
checks the three things the Pakistan pack depends on:

* the loader writes the rows with their book, edition and printed code, and a
  second load of an unchanged file writes nothing (a new edition is re-imported
  in place, and codes it dropped are deactivated, not deleted);
* the lexical matcher behind ``POST /costs/match/`` finds them with its default
  source filter;
* a cost-match run for a project in that region suggests the book item.
"""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
import pytest_asyncio
from sqlalchemy import delete, select

from app.database import async_session_factory
from app.modules.costs import pack_cost_base
from app.modules.costs.models import CostItem

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "pack_cost_base" / "test_mrs.json"
REGION = "OE_TEST_PK_RATE_BOOK"


def _manifest() -> SimpleNamespace:
    return SimpleNamespace(
        slug="test-pack",
        default_currency="PKR",
        metadata={"cost_base_dir": "cost_base", "cost_base_region": REGION, "country": "PK"},
    )


@pytest.fixture
def pack_files(monkeypatch: pytest.MonkeyPatch) -> dict[str, bytes]:
    """The pack's ``cost_base`` directory, served from memory."""
    files = {"test_mrs.json": FIXTURE.read_bytes()}

    def _files(slug: str, reldir: str) -> list[tuple[str, bytes]]:
        assert (slug, reldir) == ("test-pack", "cost_base")
        return sorted(files.items())

    monkeypatch.setattr(pack_cost_base, "_pack_cost_base_files", _files)
    return files


@pytest_asyncio.fixture
async def clean_region(app_instance):
    async with async_session_factory() as session:
        await session.execute(delete(CostItem).where(CostItem.region == REGION))
        await session.commit()
    yield
    async with async_session_factory() as session:
        await session.execute(delete(CostItem).where(CostItem.region == REGION))
        await session.commit()


async def _load() -> pack_cost_base.LoadResult:
    async with async_session_factory() as session:
        result = await pack_cost_base.load_pack_cost_base(session, _manifest())
        await session.commit()
    assert result is not None
    return result


async def _rows() -> dict[str, CostItem]:
    async with async_session_factory() as session:
        rows = (await session.execute(select(CostItem).where(CostItem.region == REGION))).scalars().all()
    return {r.code: r for r in rows}


def test_label_names_book_edition_and_district() -> None:
    source = json.loads(FIXTURE.read_text(encoding="utf-8"))["source"]
    assert pack_cost_base.book_label(source) == "Punjab MRS 1st Biannual 2099, Lahore"


def test_manifest_without_cost_base_is_ignored() -> None:
    assert pack_cost_base.pack_cost_base_settings(SimpleNamespace(metadata={}, default_currency="PKR")) is None


def test_pakistan_manifest_declares_its_cost_base() -> None:
    from app.core.partner_pack.discovery import get_pack_by_slug

    m = get_pack_by_slug("pakistan-pk")
    if m is None:
        pytest.skip("pakistan-pk pack not discoverable in this environment")
    assert pack_cost_base.pack_cost_base_settings(m) == ("cost_base", "PK", "PKR")


@pytest.mark.asyncio
async def test_loader_writes_book_rows(pack_files, clean_region) -> None:
    result = await _load()
    [book] = result.books
    assert (book.book_id, book.status, book.items, book.inserted, book.skipped) == ("test_mrs", "inserted", 4, 4, 1)

    rows = await _rows()
    item = rows["test_mrs/T-07-12"]
    assert item.source == pack_cost_base.RATE_BOOK_SOURCE
    assert item.currency == "PKR"
    assert item.unit == "m3"
    assert Decimal(item.rate) == Decimal("300")
    assert item.catalog_id is None  # shared row, visible to every user
    assert item.classification["collection"] == "Punjab MRS 1st Biannual 2099, Lahore"
    assert item.classification["department"] == "Brickwork"
    assert item.classification["book_code"] == "T-07-12"
    assert item.metadata_["rate_book"]["edition"] == "1st Biannual 2099"
    assert item.metadata_["unit_as_printed"] == "%cft"
    assert str(item.price_as_of) == "2099-01-01"


@pytest.mark.asyncio
async def test_reimport_is_idempotent_and_edition_aware(pack_files, clean_region) -> None:
    await _load()
    first = await _rows()

    again = await _load()
    assert again.books[0].status == "unchanged"
    assert again.books[0].inserted == again.books[0].updated == 0
    second = await _rows()
    assert {c: r.id for c, r in first.items()} == {c: r.id for c, r in second.items()}

    # A new edition: one rate changes, one item is dropped, one is added.
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    doc["source"]["edition"] = "2nd Biannual 2099"
    doc["items"] = [i for i in doc["items"] if i["code"] != "T-11-04"]
    doc["items"][0]["rate_pkr"] = 110.0
    doc["items"].append(
        {
            "code": "T-12-01",
            "chapter": "Flooring",
            "description": "Tuff tiles 60 mm on sand bed",
            "unit": "m2",
            "rate_pkr": 50.0,
            "kind": "item",
        }
    )
    pack_files["test_mrs.json"] = json.dumps(doc).encode("utf-8")

    updated = await _load()
    book = updated.books[0]
    assert (book.status, book.inserted, book.updated, book.deactivated) == ("updated", 1, 3, 1)
    rows = await _rows()
    assert Decimal(rows["test_mrs/T-03-01"].rate) == Decimal("110")
    assert rows["test_mrs/T-03-01"].id == first["test_mrs/T-03-01"].id
    assert rows["test_mrs/T-03-01"].classification["collection"] == "Punjab MRS 2nd Biannual 2099, Lahore"
    assert rows["test_mrs/T-11-04"].is_active is False
    assert rows["test_mrs/T-12-01"].is_active is True


@pytest.mark.asyncio
async def test_lexical_matcher_finds_book_item(pack_files, clean_region) -> None:
    from app.modules.costs.matcher import match_cwicr_items

    await _load()
    async with async_session_factory() as session:
        results = await match_cwicr_items(
            session, "brickwork cement sand mortar 1:6", unit="m3", region=REGION, top_k=3
        )
    assert results, "the default source filter must include pack rate books"
    assert results[0].code == "test_mrs/T-07-12"
    assert results[0].currency == "PKR"
    assert results[0].source_book == "Punjab MRS 1st Biannual 2099, Lahore"


@pytest.mark.asyncio
async def test_cost_match_run_for_pk_project_suggests_book_item(pack_files, clean_region, client, header) -> None:
    from app.modules.cost_match.schemas import MatchLineInput, MatchRunCreate
    from app.modules.cost_match.service import CostMatchService

    await _load()
    response = await client.post(
        "/api/v1/projects/",
        json={"name": f"PK rate book {uuid.uuid4().hex[:6]}", "region": REGION, "currency": "PKR"},
        headers=header,
    )
    assert response.status_code in (200, 201), response.text
    project = response.json()

    async with async_session_factory() as session:
        service = CostMatchService(session)
        run = await service.create_run(
            MatchRunCreate(
                project_id=uuid.UUID(project["id"]),
                name="Lahore house",
                source_locale="en",
                region=project["region"],
                candidate_limit=40,
                lines=[
                    MatchLineInput(
                        description="First class brick masonry in cement sand mortar 1:6 in foundations and plinth",
                        unit="m3",
                        quantity=Decimal("48"),
                        source_ref="",
                    )
                ],
            )
        )
        [result] = await service.result_repo.list_all_for_run(run.id)
        await session.commit()
    assert result.suggested_code == "test_mrs/T-07-12"
    assert result.suggested_currency == "PKR"
    assert result.tier != "unmatched"
