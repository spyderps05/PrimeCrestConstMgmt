# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""Demo engineering brief for the demo estate, run by ``app.core.demo_enrichment``.

Each demo project gets the brief its country's catalogue asks for: structured requirements across the
catalogue categories (with a verification method on every must), a technical concept that decides every
required topic and answers the must requirements, the area and quantity programme, and the framework
schedule: the catalogue's chain dated backwards from the operating proof, plus one milestone for every
gate of the project's phase model. Everything goes through the service, so catalogue pins, codes, audit
rows and the checks are the real ones.

The brief is submitted when the service finds nothing blocking, so the governance gate reads it as in
review. Approval goes through the gate, never through a seeder. Only projects carrying the demo marker
are touched; a project that already has a brief is skipped, so a re-run never duplicates. The story of each project is a file of the pack
(``demo/<project>-engineering_brief.json``).

The baseline requirements added in front of the story's own depend on the market. A German demo
project gets the German building baseline (DIN 18040, GEG 2024) and German documents. A Pakistani
building gets an English baseline on the Pakistani codes (Building Code of Pakistan, PEC, NEECA,
the provincial building regulations the story names), and a Pakistani road or other infrastructure
project gets none: its story carries the requirements that fit it. A story may pin either choice
with ``"baseline"`` (``"de"``, ``"pk_building"`` or ``"none"``) and ``"locale"``.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Iterable
from datetime import date, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# (category, entity, attribute, constraint_type, value, unit, priority, verification, originator, role, source)
_REQ = tuple[str, str, str, str, str, str, str, str, str, str, str]

_COMMON: tuple[_REQ, ...] = (
    (
        "performance",
        "Gebäude",
        "Brutto-Grundfläche",
        "max",
        "{bgf}",
        "m2",
        "must",
        "analysis",
        "Bauherr",
        "client",
        "Raumprogramm",
    ),
    (
        "performance",
        "Tragwerk",
        "Nutzlast Regelgeschoss",
        "min",
        "{live}",
        "kN/m2",
        "must",
        "analysis",
        "Tragwerksplanung",
        "designer",
        "DIN EN 1991-1-1",
    ),
    (
        "standards",
        "Brandschutz",
        "Gebäudeklasse",
        "equals",
        "{gk}",
        "",
        "must",
        "inspection",
        "Brandschutzgutachter",
        "authority",
        "{lbo}",
    ),
    (
        "standards",
        "Barrierefreiheit",
        "Anforderung",
        "equals",
        "DIN 18040",
        "",
        "must",
        "inspection",
        "Bauherr",
        "client",
        "{lbo}",
    ),
    (
        "energy_efficiency",
        "Gebäudehülle",
        "Energiestandard",
        "equals",
        "{energy}",
        "",
        "must",
        "analysis",
        "Bauherr",
        "client",
        "GEG 2024",
    ),
    (
        "energy_efficiency",
        "Wärmeversorgung",
        "Erneuerbarer Anteil",
        "min",
        "65",
        "%",
        "must",
        "analysis",
        "Energieplanung",
        "designer",
        "GEG 2024",
    ),
    (
        "availability",
        "Aufzüge",
        "Verfügbarkeit",
        "min",
        "98",
        "%",
        "should",
        "demonstration",
        "Betreiber",
        "client",
        "Betriebskonzept",
    ),
    (
        "site_conditions",
        "Baugrund",
        "Gründungsempfehlung",
        "equals",
        "Bodenplatte mit Teilunterkellerung",
        "",
        "should",
        "inspection",
        "Baugrundgutachter",
        "designer",
        "Baugrundgutachten",
    ),
    (
        "operation_maintenance",
        "Technik",
        "Wartungszugang je Anlage",
        "exists",
        "",
        "",
        "should",
        "inspection",
        "Facility Management",
        "client",
        "Betriebskonzept",
    ),
    (
        "safety_security",
        "Außenanlagen",
        "Beleuchtung Zugänge",
        "min",
        "10",
        "lx",
        "could",
        "test",
        "Bauherr",
        "client",
        "DIN EN 12464-2",
    ),
)


# The Pakistani building baseline. English, on the codes a Pakistani building is approved and checked against.
# ``{lbo}`` is the provincial or authority building regulation the story names (LDA, SBCA/Karachi, Punjab bye-laws).
_COMMON_PK_BUILDING: tuple[_REQ, ...] = (
    (
        "performance",
        "Building",
        "Gross floor area",
        "max",
        "{bgf}",
        "m2",
        "must",
        "analysis",
        "Client",
        "client",
        "Approved space programme",
    ),
    (
        "performance",
        "Structure",
        "Live load, typical floor",
        "min",
        "{live}",
        "kN/m2",
        "must",
        "analysis",
        "Structural engineer",
        "designer",
        "Building Code of Pakistan (loading provisions)",
    ),
    (
        "standards",
        "Structure",
        "Seismic design",
        "equals",
        "BCP-SP 2021 seismic zone of the site",
        "",
        "must",
        "analysis",
        "Structural engineer",
        "designer",
        "Building Code of Pakistan, Seismic Provisions (BCP-SP 2021)",
    ),
    (
        "standards",
        "Building approval",
        "Occupancy classification",
        "equals",
        "{gk}",
        "",
        "must",
        "inspection",
        "Building control authority",
        "authority",
        "{lbo}",
    ),
    (
        "standards",
        "Design professionals",
        "Design signed by PEC-registered engineers",
        "exists",
        "",
        "",
        "must",
        "inspection",
        "Pakistan Engineering Council",
        "authority",
        "PEC Act 1976 and PEC bye-laws",
    ),
    (
        "standards",
        "Accessibility",
        "Requirement",
        "equals",
        "Accessibility Code of Pakistan 2006",
        "",
        "must",
        "inspection",
        "Client",
        "client",
        "{lbo}",
    ),
    (
        "energy_efficiency",
        "Building envelope",
        "Energy standard",
        "equals",
        "{energy}",
        "",
        "must",
        "analysis",
        "Client",
        "client",
        "NEECA, Building Code of Pakistan (Energy Provisions)",
    ),
    (
        "site_conditions",
        "Subsoil",
        "Foundation design from a geotechnical investigation",
        "exists",
        "",
        "",
        "should",
        "inspection",
        "Geotechnical engineer",
        "designer",
        "Geotechnical investigation report",
    ),
    (
        "operation_maintenance",
        "Building services",
        "Maintenance access to each plant item",
        "exists",
        "",
        "",
        "should",
        "inspection",
        "Facility management",
        "client",
        "Operation concept",
    ),
    (
        "safety_security",
        "External works",
        "Lighting at entrances",
        "min",
        "10",
        "lx",
        "could",
        "test",
        "Client",
        "client",
        "BS EN 12464-2",
    ),
)

# The baseline set for each market kind. A road or other infrastructure project takes none: a building baseline
# (floor area, occupancy, accessibility) means nothing there, and its story carries what fits it.
_BASELINES: dict[str, tuple[_REQ, ...]] = {"de": _COMMON, "pk_building": _COMMON_PK_BUILDING, "none": ()}

# Words in a story's facility class or a project type that mark a project as infrastructure rather than a building.
_INFRA_WORDS = ("road", "highway", "bridge", "culvert", "carriageway", "pipeline", "canal", "railway", "infrastructure")

_STUDY_LABELS: dict[str, dict[str, str]] = {
    "de": {
        "subject": "Gegenstand",
        "content": "Inhalt",
        "scope": "Untersuchungsumfang",
        "result": "Ergebnis",
        "assessment": "Bewertung",
        "author": "Verfasser",
        "date": "Datum",
        "suitable": "geeignet",
        "conditional": "bedingt geeignet",
        "unsuitable": "nicht geeignet",
        "date_format": "%d.%m.%Y",
    },
    "en": {
        "subject": "Subject",
        "content": "Content",
        "scope": "Scope of investigation",
        "result": "Result",
        "assessment": "Assessment",
        "author": "Author",
        "date": "Date",
        "suitable": "suitable",
        "conditional": "conditionally suitable",
        "unsuitable": "unsuitable",
        "date_format": "%d/%m/%Y",
    },
}


def _is_pakistani(project: Any) -> bool:
    region = str(getattr(project, "region", "") or "").strip().upper()
    country = str(getattr(project, "country_code", "") or "").strip().upper()
    currency = str(getattr(project, "currency", "") or "").strip().upper()
    return region == "PK" or country == "PK" or currency == "PKR"


def _is_infrastructure(project: Any, story: dict[str, Any]) -> bool:
    text = " ".join(
        str(x or "") for x in (getattr(project, "project_type", None), (story.get("format") or {}).get("gk"))
    ).lower()
    return any(word in text for word in _INFRA_WORDS)


def _market(project: Any, story: dict[str, Any]) -> tuple[str, str]:
    """``(baseline kind, document locale)`` for this project: the story's own choice first, else its market."""
    kind = story.get("baseline")
    if kind not in _BASELINES:
        if _is_pakistani(project):
            kind = "none" if _is_infrastructure(project, story) else "pk_building"
        else:
            kind = "de"
    locale = story.get("locale")
    if not isinstance(locale, str) or not locale.strip():
        locale = "de" if kind == "de" else "en"
    return kind, locale.strip()


def _requirement_rows(kind: str, story: dict[str, Any]) -> list[_REQ]:
    """The baseline of ``kind``, then the story's own rows. A story row replaces a baseline row on the same subject."""
    extra = [tuple(str(r.get(k, "") or "") for k in _KEYS) for r in story.get("requirements", [])]
    own = {(row[1].strip().lower(), row[2].strip().lower()) for row in extra}
    base = [row for row in _BASELINES[kind] if (row[1].strip().lower(), row[2].strip().lower()) not in own]
    return [*base, *extra]  # type: ignore[list-item]


async def _study_report(
    session: AsyncSession, project_id: uuid.UUID, actor: Any, row: dict[str, Any], locale: str = "de"
) -> uuid.UUID:
    """The study report as a PDF in the documents module, written through its own upload path."""
    from io import BytesIO

    from starlette.datastructures import UploadFile

    from app.core.register_export import RegisterColumn
    from app.modules.documents.service import DocumentService
    from app.modules.engineering_brief import export as ex

    title, scope, author, offset = row["title"], row["scope"], row["author"], row["days"]
    result, conclusion = row["result"], row["conclusion"]
    lang = "de" if locale.lower().startswith("de") else "en"
    t = _STUDY_LABELS[lang]
    day = date.today() + timedelta(days=offset)
    doc = ex._doc(
        title,
        [RegisterColumn(t["subject"], weight=1, wrap=True), RegisterColumn(t["content"], weight=4, wrap=True)],
        [[t["scope"], scope], [t["result"], result], [t["assessment"], t.get(conclusion, "")]],
        [(t["author"], author), (t["date"], day.strftime(t["date_format"]))],
        lang,
    )
    name = title.replace("/", "-")
    upload = UploadFile(file=BytesIO(ex.render(doc, "pdf")), filename=f"{name}.pdf")
    document = await DocumentService(session).upload_document(project_id, upload, "other", str(actor))
    return document.id


_KEYS = (
    "category",
    "entity",
    "attribute",
    "constraint_type",
    "constraint_value",
    "unit",
    "priority",
    "verification_method",
    "originator",
    "originator_role",
    "source_ref",
)


def _fill(row: _REQ, fmt: dict[str, str]) -> _REQ:
    return tuple(c.format(**fmt) if "{" in c else c for c in row)  # type: ignore[return-value]


async def _seed_project(session: AsyncSession, project_id: uuid.UUID, story: dict[str, Any]) -> dict[str, int]:
    from app.modules.engineering_brief.service import EngineeringBriefService
    from app.modules.projects.models import Project

    project = await session.get(Project, project_id)
    actor = project.owner_id
    kind, locale = _market(project, story)
    svc = EngineeringBriefService(session)
    counts = {
        "requirements": 0,
        "concepts": 0,
        "programme": 0,
        "milestones": 0,
        "submitted": 0,
        "gates_bound": 0,
        "need_dates_bound": 0,
        "studies": 0,
        "issued": 0,
    }

    await svc.set_brief(
        project_id,
        actor_id=actor,
        tenant_id=None,
        title=story["title"],
        summary=story["summary"],
        operation_proof_date=date.today() + timedelta(days=int(story.get("operation_proof_days") or 760)),
    )

    created: list[Any] = []
    for row in _requirement_rows(kind, story):
        cat, entity, attr, ctype, value, unit, prio, verif, orig, role, src = _fill(row, story["format"])
        data = {
            "category": cat,
            "entity": entity,
            "attribute": attr,
            "constraint_type": ctype,
            "constraint_value": value,
            "unit": unit,
            "priority": prio,
            "verification_method": verif,
            "originator": orig,
            "originator_role": role,
            "source_ref": src,
        }
        created.append((prio, await svc.create_requirement(project_id, data, actor)))
        counts["requirements"] += 1
    musts = [r.id for prio, r in created if prio == "must"]

    # The concept: one decided item for every topic of the profile, the first carrying the musts it answers.
    brief = await svc.require_brief(project_id)
    catalogue = await svc.catalogue_for(brief)
    titles = {t.code: t for t in catalogue.concept_topics}
    first = True
    for code, decision in story["topics"].items():
        if code not in titles:
            continue
        await svc.create_concept(
            project_id,
            {
                "topic_code": code,
                "title": decision.split(",")[0].split(".")[0][:120],
                "description": "",
                "decision": decision,
                "requirement_ids": musts if first else [],
            },
            actor,
        )
        first = False
        counts["concepts"] += 1

    for line in story["programme"]:
        await svc.create_programme(project_id, dict(line), actor)
        counts["programme"] += 1

    made = await svc.milestones_from_catalogue(project_id, None, actor)
    counts["milestones"] += len(made)
    if catalogue.gate_kind is not None:
        gates = await svc.milestones_from_gates(project_id, actor, locale)
        counts["milestones"] += len(gates)
        # A gate without a target date still gets a believable one: after the previous gate and never before today.
        # A gate already decided was decided on its day; it is not given a date ahead of it.
        previous = date.today()
        decided = await _decided_gate_codes(svc, project_id)
        for row in await svc.milestone_views(project_id):
            if not row["gate_code"]:
                continue
            if row["planned_date"] is None and row["gate_code"] in decided:
                await svc.update_milestone(project_id, uuid.UUID(row["id"]), {"planned_date": previous}, actor)
            elif row["planned_date"] is None:
                previous = previous + timedelta(days=75)
                await svc.update_milestone(project_id, uuid.UUID(row["id"]), {"planned_date": previous}, actor)
            else:
                previous = max(previous, date.fromisoformat(row["planned_date"]))

    # The schedule module takes the milestones and owns the date of every undecided gate. A decided gate
    # keeps what it was decided with; nothing may be refused here, or the demo would show an unbound gate.
    published = await svc.publish_schedule(project_id, actor)
    if published["gates_skipped"]:
        logger.warning("engineering brief demo: gates not bound for %s: %s", project_id, published["gates_skipped"])
    counts["gates_bound"] = len(published["gates_bound"])
    await _complete_decided_gate_milestones(session, svc, project_id)
    counts["need_dates_bound"] = await _bind_nearest_package(session, project_id)

    for row in story.get("studies", []):
        await svc.create_study(
            project_id,
            {
                "kind": row["kind"],
                "title": row["title"],
                "scope": row["scope"],
                "author": row["author"],
                "study_date": date.today() + timedelta(days=row["days"]),
                "result": row["result"],
                "conclusion": row["conclusion"],
                "document_id": await _study_report(session, project_id, actor, row, locale),
            },
            actor,
        )
        counts["studies"] += 1

    # Submit only what the checks accept; a brief with a blocking finding stays the draft somebody is on.
    blocking = [f for f in await svc.submission_findings(project_id) if f.severity == "error"]
    if not blocking:
        try:
            async with session.begin_nested():
                await svc.submit(project_id, actor)
            counts["submitted"] = 1
            await svc.issue_specification(project_id, actor, story.get("issue_note", ""), locale=locale)
            counts["issued"] = 1
        except Exception:
            logger.info("engineering brief demo left as draft for %s", project_id, exc_info=True)
    return counts


# How far a package's typed need date may be from a milestone for the demo to bind it without moving anything visible.
_BIND_WINDOW_DAYS = 5


async def _bind_nearest_package(session: AsyncSession, project_id: uuid.UUID) -> int:
    """Bind the one package whose need date already sits at a published milestone to that milestone.

    Only a package within a few days of a milestone is bound, and it takes the milestone's date, so
    every other date of the demo stays where its story put it. Returns 1 when a package was bound.
    """
    from app.modules.engineering_brief.models import FrameMilestone
    from app.modules.procurement_concept.models import AwardPackage
    from app.modules.schedule.models import Activity

    activity_ids = [
        m.activity_id
        for m in (
            await session.execute(select(FrameMilestone).where(FrameMilestone.project_id == project_id))
        ).scalars()
        if m.activity_id is not None
    ]
    if not activity_ids:
        return 0
    starts = {
        row.id: str(row.start_date)[:10]
        for row in (
            await session.execute(select(Activity.id, Activity.start_date).where(Activity.id.in_(activity_ids)))
        )
        if row.start_date
    }
    packages = (
        (
            await session.execute(
                select(AwardPackage).where(
                    AwardPackage.project_id == project_id,
                    AwardPackage.need_date.is_not(None),
                    AwardPackage.need_activity_id.is_(None),
                )
            )
        )
        .scalars()
        .all()
    )
    best: tuple[int, Any, uuid.UUID, str] | None = None
    for pkg in packages:
        try:
            need = date.fromisoformat(str(pkg.need_date)[:10])
        except ValueError:
            continue
        for activity_id, start in starts.items():
            gap = abs((date.fromisoformat(start) - need).days)
            if gap <= _BIND_WINDOW_DAYS and (best is None or gap < best[0]):
                best = (gap, pkg, activity_id, start)
    if best is None:
        return 0
    _, pkg, activity_id, start = best
    pkg.need_activity_id = activity_id
    pkg.need_date = start
    await session.flush()
    return 1


def _story_of(demo_id: str) -> dict[str, Any] | None:
    """The pack story of this demo project, or ``None`` when the active pack has none or it is unusable."""
    from app.modules.project_governance.public import demo_module_story

    story = demo_module_story(demo_id, "engineering_brief")
    needed = ("title", "summary", "format", "topics", "programme")
    return story if story and all(story.get(k) for k in needed) else None


async def seed_engineering_brief_demo(session: AsyncSession, project_ids: Iterable[uuid.UUID]) -> dict[str, int]:
    """Seed the brief of every demo project in ``project_ids`` that has none. The caller commits."""
    from app.core.demo_marker import demo_id_of
    from app.modules.engineering_brief.models import EngineeringBrief
    from app.modules.projects.models import Project

    totals = {
        "projects": 0,
        "requirements": 0,
        "concepts": 0,
        "programme": 0,
        "milestones": 0,
        "submitted": 0,
        "gates_bound": 0,
        "need_dates_bound": 0,
        "studies": 0,
        "issued": 0,
    }
    ids = list(project_ids)
    if not ids:
        return totals
    rows = (await session.execute(select(Project.id, Project.metadata_).where(Project.id.in_(ids)))).all()
    for pid, meta in rows:
        demo_id = demo_id_of(meta)
        if not demo_id:
            continue
        has = (
            await session.execute(select(EngineeringBrief.id).where(EngineeringBrief.project_id == pid))
        ).scalar_one_or_none()
        if has is not None:
            continue
        story = _story_of(demo_id)
        if story is None:
            # A demo project the pack tells no story for gets no brief: none is invented from another project.
            logger.info("engineering brief demo: no story for %s, skipped", demo_id)
            continue
        try:
            async with session.begin_nested():
                counts = await _seed_project(session, pid, story)
        except Exception:
            # One project that cannot be seeded must not take the rest of the demo estate with it.
            logger.warning("engineering brief demo seed skipped for %s", pid, exc_info=True)
            continue
        totals["projects"] += 1
        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + v
    return totals


async def _decided_gate_codes(svc: Any, project_id: uuid.UUID) -> set[str]:
    return {str(g["code"]) for g in await svc._gates(project_id) if g["status"] == "decided"}


async def _complete_decided_gate_milestones(session: AsyncSession, svc: Any, project_id: uuid.UUID) -> int:
    """Mark the published milestone of every decided gate as reached.

    The schedule reads an unfinished milestone as still ahead, so without this the project hub names a gate
    that was decided as the next milestone. Returns how many activities were completed.
    """
    from app.modules.schedule.models import Activity

    decided = await _decided_gate_codes(svc, project_id)
    done = 0
    for row in await svc.milestone_views(project_id):
        if row["gate_code"] not in decided or row["activity_id"] is None:
            continue
        act = await session.get(Activity, row["activity_id"])
        if act is not None and act.status != "completed":
            act.status = "completed"
            act.progress_pct = "100"
            done += 1
    await session.flush()
    return done
