"""Legacy launcher alias.

Kept so ``python -m openconstructionerp`` from installs and scripts that predate
the PrimeCrest rename keeps working. New code and docs use ``primecrest``.
"""

from __future__ import annotations

from app.cli import main

__all__ = ["main"]
