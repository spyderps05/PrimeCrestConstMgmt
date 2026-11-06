"""​‌‍⁠​‌‍⁠​‌‍⁠​‌‍⁠The AGPL-3.0 text has to be present, verbatim, and reachable by the build.

That was the rule while the project was distributed under AGPL-3.0. Since
2026-11-06 PrimeCrest ships under a proprietary commercial licence held by
Spyder Solutions (``license = "LicenseRef-Proprietary"`` in ``pyproject.toml``
and the "Other/Proprietary License" trove classifier), so what has to be present
and reachable by the build is that proprietary licence, and no AGPL text may sit
where it belongs. Up to and including 15.9.1 the built wheel's ``dist-info`` had
no licence file and the container image carried none either; this module keeps
the licence the product is actually distributed under travelling with both.

Two copies of the text exist, and they exist for different consumers:

* ``LICENSE`` at the repo root, which is where the licence conventionally lives,
  where GitHub's detector reads it, and what ``desktop/src-tauri/tauri.conf.json``
  points the installer at.
* ``backend/LICENSE``, which is the one the wheel can actually use. PEP 639
  resolves ``license-files`` against the project root, and for this build that is
  ``backend/``, which cannot reach ``../LICENSE``.

NOTICE is the same arrangement for the same reason, and it was missing for
longer. The published 16.0.0 wheel holds 3860 entries and NOTICE is not among
them, so a pip install conveys the licence text and no attribution index at all.
What makes that particular absence awkward is that six bundled font and font
engine licences do travel in that wheel, inside ``app/`` where they sit under
the package directory rather than beside it, and NOTICE is the file that says
what they are, which bundled binaries carry code nobody declared, and where the
per-release inventory is published. The one file a reader would go to first was
the one they could not reach.

Duplication is the deliberate trade, and this module is what stops it drifting.
The licence text changes only when its owner changes it, so the only way the
two licence copies can diverge is by accident, which is exactly what an
assertion is for. NOTICE is the opposite case and needs the assertion more: it
is edited every time a dependency starts or stops bundling somebody else's
object code, and an edit that lands in one copy and not the other leaves the
wheel conveying a stale account of what it contains.

Line endings are normalised before comparing. ``core.autocrlf`` is on for many
contributors, so the working-tree bytes differ by platform even though the git
blob does not; what has to hold is that the text is the same, not that a
checkout picked one convention.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND = REPO_ROOT / "backend"
ROOT_LICENCE = REPO_ROOT / "LICENSE"
WHEEL_LICENCE = BACKEND / "LICENSE"
ROOT_NOTICE = REPO_ROOT / "NOTICE"
WHEEL_NOTICE = BACKEND / "NOTICE"
PYPROJECT = BACKEND / "pyproject.toml"

# Every file the wheel is told to convey, in the order it declares them. Both
# are resolved against ``backend/``, so both have to exist there, and nothing
# in the build will say so if one does not. These are glob patterns: hatchling
# 1.32.0 drops a pattern that matches no file without a warning, and the build
# exits 0 carrying one ``License-File`` instead of two. Measured, not read off
# the spec. That makes the existence check at the bottom of this module the
# only thing between the declaration and a quietly thinner wheel.
EXPECTED_LICENCE_FILES = ["LICENSE", "NOTICE"]

# Section headings NOTICE has to keep. Picked because each one is the answer to
# a question somebody actually arrives with, so a file that lost one would be
# answering fewer questions while still looking like a notice.
NOTICE_MARKERS = [
    "Third-Party Software",
    "AGPL Cascade",
    "Trademarks",
    "Data Sources",
    "Bundled Font Software",
    "Native Binaries Inside Python Wheels",
    "Disclaimer of Warranty",
]

# Landmarks of the proprietary licence. Each is a statement the product's legal
# position rests on, so a file missing one would be the wrong licence shipped
# under the right name.
REQUIRED_MARKERS = [
    "PrimeCrest Construction Management",
    "Copyright \u00a9 2026 Spyder Solutions. All rights reserved.",
    "proprietary software owned by",
    "without prior written permission from",
    'PROVIDED "AS IS"',
    "Third-party components bundled with this software remain under their own",
]

# Landmarks of the GNU Affero licence the project used to ship. None of them may
# appear in the product's own licence file any more.
FORBIDDEN_MARKERS = [
    "GNU AFFERO GENERAL PUBLIC LICENSE",
    "AGPL",
    "Remote Network Interaction",
]


def _text(path: Path) -> str:
    assert path.is_file(), f"missing licence file: {path}"
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


@pytest.mark.parametrize("path", [ROOT_LICENCE, WHEEL_LICENCE], ids=["root", "backend"])
def test_licence_file_is_the_proprietary_licence(path: Path) -> None:
    """Each copy is the proprietary licence, not the AGPL text it replaced."""
    text = _text(path)

    for marker in REQUIRED_MARKERS:
        assert marker in text, f"{path.relative_to(REPO_ROOT)} is missing licence landmark: {marker!r}"

    for marker in FORBIDDEN_MARKERS:
        assert marker not in text, (
            f"{path.relative_to(REPO_ROOT)} still carries {marker!r}. PrimeCrest is proprietary "
            "software under a commercial licence and the AGPL text must not ship as its licence."
        )


def test_the_wheel_metadata_declares_the_proprietary_licence() -> None:
    """The METADATA expression and the trove classifier agree with LICENSE."""
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    assert re.search(r'^license\s*=\s*"LicenseRef-Proprietary"\s*$', pyproject, re.MULTILINE), (
        'backend/pyproject.toml must declare license = "LicenseRef-Proprietary".'
    )
    assert "License :: Other/Proprietary License" in pyproject
    assert "License :: OSI Approved :: GNU Affero" not in pyproject


def test_the_two_licence_copies_are_identical() -> None:
    """``backend/LICENSE`` exists only so the wheel can carry the root one."""
    assert _text(ROOT_LICENCE) == _text(WHEEL_LICENCE), (
        "LICENSE and backend/LICENSE have drifted apart. backend/LICENSE is a copy of the "
        "repo-root licence made because PEP 639 cannot reach outside the project root; "
        "copy the root file over it rather than editing either in place."
    )


def test_the_two_notice_copies_are_identical() -> None:
    """``backend/NOTICE`` exists only so the wheel can carry the root one."""
    assert _text(ROOT_NOTICE) == _text(WHEEL_NOTICE), (
        "NOTICE and backend/NOTICE have drifted apart. backend/NOTICE is a copy of the "
        "repo-root notice made because PEP 639 cannot reach outside the project root; copy the "
        "root file over it rather than editing either in place. A notice edited on one side only "
        "leaves the wheel describing a set of bundled binaries that is no longer the one it holds."
    )


@pytest.mark.parametrize("path", [ROOT_NOTICE, WHEEL_NOTICE], ids=["root", "backend"])
def test_notice_is_the_attribution_index_and_not_a_pointer(path: Path) -> None:
    """A stub sitting where the notice belongs looks like the thing it replaces."""
    text = _text(path)

    for marker in NOTICE_MARKERS:
        assert marker in text, f"{path.relative_to(REPO_ROOT)} is missing NOTICE section: {marker!r}"

    # The file runs to roughly 38 KB. The floor is far below that so ordinary
    # editing cannot trip it, and far above anything that could be written as a
    # summary pointing somewhere else.
    assert len(text) > 20_000, (
        f"{path.relative_to(REPO_ROOT)} is {len(text)} characters, too short to be the attribution "
        "index. A pointer must not occupy the place the notice belongs."
    )


@pytest.mark.parametrize("path", [ROOT_NOTICE, WHEEL_NOTICE], ids=["root", "backend"])
def test_every_bundled_licence_notice_names_exists(path: Path) -> None:
    """NOTICE points at committed licence texts, and those have to be there.

    ``app/core/licenses/`` holds the texts for object code that arrives inside
    somebody else's wheel with no notice of its own: HarfBuzz compiled into
    uharfbuzz, PostgreSQL inside pixeltable-pgserver, OpenSSL inside both
    psycopg2-binary and cryptography. NOTICE is what tells a reader those files
    exist and which binary each covers, so a path here that names nothing is a
    notice claiming an attribution the artefact does not carry.
    """
    # The last character has to be one a filename can actually end on. A dot is
    # allowed inside the path because a licence text may carry an extension, but
    # NOTICE is prose and two of these paths end a sentence, so a trailing run of
    # dots belongs to the sentence rather than to the file. Matching it produced
    # a failure naming ``LICENSE_GPL_3_0.`` and ``LICENSE_OPENSSL_SSLEAY.`` while
    # both files sat in the tree correctly named, which is the gate failing on
    # its own data: the notice was right, the files were right, and the reader
    # was wrong. The third reference passed only because it happens to end a line.
    referenced = sorted(set(re.findall(r"backend/(app/core/licenses/[A-Za-z0-9_./-]*[A-Za-z0-9_-])", _text(path))))

    # Anti-vacuity: seven entries name a licence text today, not the three this
    # said before the reader was fixed. Two of the seven were being read with a
    # sentence's full stop attached and a further four were never reached at
    # all, so the number written here had been describing the reader rather than
    # the notice. The floor stays well under seven because a dependency that
    # stops bundling somebody else's object code should be able to drop its
    # entry without failing this, but note what that costs: the assertion below
    # catches the section being deleted and would not catch it being gutted.
    # An empty match set would otherwise pass the loop on any file at all.
    assert len(referenced) >= 2, (
        f"{path.relative_to(REPO_ROOT)} names {referenced} under app/core/licenses. The notice used "
        "to point at a committed licence text for every bundled binary that ships without one, so a "
        "set this small means the section was removed rather than that the gap closed."
    )

    missing = [name for name in referenced if not (BACKEND / name).is_file()]
    assert not missing, (
        f"{path.relative_to(REPO_ROOT)} points at licence texts that are not in the tree: {missing}. "
        "Either restore the file or stop claiming the attribution travels with the binary."
    )


def test_the_wheel_build_is_told_to_ship_the_licence_and_the_notice() -> None:
    """Without ``license-files`` the text sits in the tree and never travels.

    ``license = "LicenseRef-Proprietary"`` writes ``License-Expression`` into METADATA
    and ships no bytes. This is the line that puts the text at
    ``*.dist-info/licenses/LICENSE`` inside the wheel, and NOTICE beside it.

    Read as a list rather than matched as one literal string, because the
    previous pinned pattern would have failed on the day a second entry was
    added, and failed by looking like the declaration had been removed.
    """
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    declaration = re.search(r"^license-files\s*=\s*\[(.*?)\]", pyproject, re.MULTILINE | re.DOTALL)
    assert declaration, (
        "backend/pyproject.toml no longer declares license-files, so the built wheel conveys no "
        "licence text for the licence it declares and no attribution index for what it bundles."
    )

    declared = re.findall(r'"([^"]+)"', declaration.group(1))
    assert declared == EXPECTED_LICENCE_FILES, (
        f"backend/pyproject.toml declares license-files = {declared}, expected "
        f"{EXPECTED_LICENCE_FILES}. Both are resolved against backend/, so both have to be committed "
        "copies of the repo-root files."
    )

    absent = [name for name in declared if not (BACKEND / name).is_file()]
    assert not absent, (
        f"license-files names {absent}, which do not exist under backend/. hatchling resolves these "
        "against the project root as glob patterns and silently drops any that match nothing, so the "
        "build will go green and the wheel will convey one fewer licence than it claims."
    )
