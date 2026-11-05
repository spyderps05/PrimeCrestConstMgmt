"""Installed distribution name of the PrimeCrest backend.

The wheel is published as ``primecrest``. Installs made before the rename
carry the upstream distribution name instead, so version lookups try the
legacy names too rather than reporting "not installed".
"""

from __future__ import annotations

import importlib.metadata

DIST_NAME = "primecrest"
LEGACY_DIST_NAMES: tuple[str, ...] = ("openconstructionerp",)


def installed_version() -> str:
    """Return the installed backend version, or raise ``PackageNotFoundError``.

    ``importlib.metadata.version`` is looked up on every call (not bound at
    import) so callers and tests that patch it see the patched function.
    """
    for name in (DIST_NAME, *LEGACY_DIST_NAMES):
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    raise importlib.metadata.PackageNotFoundError(DIST_NAME)
