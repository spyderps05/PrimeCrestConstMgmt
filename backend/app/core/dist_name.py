"""Installed distribution name of the PrimeCrest backend.

The wheel is published as ``primecrest``. Installs made before the rename
carry the upstream distribution name instead, so version lookups try the
legacy names too rather than reporting "not installed".
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

DIST_NAME = "primecrest"
LEGACY_DIST_NAMES: tuple[str, ...] = ("openconstructionerp",)


def installed_version() -> str:
    """Return the installed backend version, or raise ``PackageNotFoundError``."""
    for name in (DIST_NAME, *LEGACY_DIST_NAMES):
        try:
            return version(name)
        except PackageNotFoundError:
            continue
    raise PackageNotFoundError(DIST_NAME)
