# DDC-CWICR-OE: DataDrivenConstruction · PrimeCrest
# Copyright (c) 2026 Artem Boiko / DataDrivenConstruction
"""Importer for a Punjab Market Rate System file the operator downloaded.

The pack does not ship the government PDF and it does not ship a third-party
reprint. This reader takes a CSV already in the official column shape and
keeps a row only when the row names an official host.
"""

from __future__ import annotations

import csv
import io
from urllib.parse import urlparse

__all__ = ["MRS_COLUMNS", "import_mrs_csv"]

MRS_COLUMNS = (
    "district",
    "period",
    "chapter",
    "item_number",
    "description",
    "unit",
    "labour_rate",
    "composite_rate",
    "material_rate",
    "equipment_rate",
    "specification_number",
    "source_url",
)

_REQUIRED = (
    "district",
    "period",
    "chapter",
    "item_number",
    "description",
    "unit",
    "labour_rate",
    "composite_rate",
    "specification_number",
    "source_url",
)

_OFFICIAL_HOSTS = frozenset({"finance.punjab.gov.pk", "nha.gov.pk"})


def _host(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def import_mrs_csv(text: str) -> list[dict[str, str]]:
    """Read one official-period CSV.

    Material and equipment may be blank. Labour, composite, the specification
    number and the source address may not. A source that is not the Finance
    Department portal or the NHA document host is refused, so a third-party
    dump cannot be loaded by renaming the file.
    """
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise ValueError("The rate file has no header row.")
    missing = [name for name in _REQUIRED if name not in reader.fieldnames]
    if missing:
        raise ValueError("The rate file is missing columns: " + ", ".join(missing))
    rows: list[dict[str, str]] = []
    for index, raw in enumerate(reader, start=2):
        row = {key: (raw.get(key) or "").strip() for key in MRS_COLUMNS}
        blank = [name for name in _REQUIRED if not row[name]]
        if blank:
            raise ValueError(f"Row {index} is missing {', '.join(blank)}.")
        if _host(row["source_url"]) not in _OFFICIAL_HOSTS:
            raise ValueError(
                f"Row {index} does not cite the Finance Department or NHA. Third-party rate dumps are not loaded."
            )
        chapter = row["chapter"]
        if not chapter.isdigit() or not 1 <= int(chapter) <= 27:
            raise ValueError(f"Row {index} chapter must be a number from 1 to 27.")
        rows.append(row)
    return rows
