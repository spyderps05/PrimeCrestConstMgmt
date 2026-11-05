"""PrimeCrest Pakistan pack by Spyder Solutions (PKR, GST, provincial sales tax, PEC, PPRA, MRS/CSR, Urdu).

Exports a module-level ``MANIFEST`` referenced from ``pyproject.toml``::

    [project.entry-points."openconstructionerp.partner_packs"]
    pakistan-pk = "openconstructionerp_pakistan_pk:MANIFEST"

    [project.entry-points."primecrest.partner_packs"]
    pakistan-pk = "openconstructionerp_pakistan_pk:MANIFEST"
"""

from __future__ import annotations

from .manifest import MANIFEST

__all__ = ["MANIFEST"]
__version__ = "0.2.0"
