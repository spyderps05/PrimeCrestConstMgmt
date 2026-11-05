"""Brand-named launcher package.

This package exists so ``python -m primecrest`` works straight after
``pip install primecrest`` even when the pip console-script directory is
not on PATH. That is the common situation on Windows, where Python's Scripts
folder is often not added to PATH, so the bare ``primecrest`` command is
not found in a fresh shell. The real application and CLI live in the ``app``
package; this is a thin shim that re-exports the CLI entry point.
"""

from __future__ import annotations

from app.cli import main

__all__ = ["main"]
