"""Keep the developer's own AI keys out of tests that assert on "no key".

``app.modules.ai.ai_client`` falls back to provider keys in the environment
(``ANTHROPIC_API_KEY``, ``GEMINI_API_KEY``, ``GOOGLE_API_KEY`` ...) and in
``~/.openestimate/config.json`` when the database holds none. A test that
expects "No AI API key configured" (or the offline degradation it causes) then
passes in CI and fails on any machine where a key happens to be exported.

Use :func:`isolate_ai_keys` from an autouse fixture: it removes every variable
the resolver reads and points the home directory at an empty temp dir, so the
config-file fallback finds nothing either. A test that wants a key sets it
itself with ``monkeypatch.setenv`` after this has run.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def isolate_ai_keys(monkeypatch: pytest.MonkeyPatch, home: Path) -> None:
    from app.modules.ai.ai_client import _ENV_KEY_NAMES

    for _provider, env_names in _ENV_KEY_NAMES:
        for env_name in env_names:
            monkeypatch.delenv(env_name, raising=False)
    home.mkdir(parents=True, exist_ok=True)
    # ``os.path.expanduser("~")`` reads USERPROFILE on Windows and HOME elsewhere.
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
