"""The demo floor plan speaks the language of the project's market.

The DWG Takeoff demo drawing used to be a German Grundriss for every demo
project, so a Pakistani estimator opening the Lahore house met "Wohnen" and
"Schlafen" on the first drawing they saw. German-language markets keep the
Grundriss; every other market gets an English house plan.
"""

from __future__ import annotations

import re

import pytest

from app.scripts.seed_dwg_drawing import _build_demo_dxf, plan_language

ezdxf = pytest.importorskip("ezdxf", reason="the demo drawing is authored with ezdxf")


@pytest.mark.parametrize(
    ("country", "locale", "expected"),
    [
        ("PK", "en", "en"),
        ("GB", "en", "en"),
        (None, None, "en"),
        ("", "", "en"),
        ("DE", "en", "de"),
        ("AT", "de", "de"),
        ("CH", "fr", "de"),
        ("US", "de-DE", "de"),
    ],
)
def test_plan_language_follows_the_market(country, locale, expected) -> None:
    assert plan_language(country, locale) == expected


def _texts(path) -> list[str]:
    doc = ezdxf.readfile(str(path))
    return [e.dxf.text for e in doc.modelspace().query("TEXT")]


def test_english_plan_names_its_rooms_in_english(tmp_path) -> None:
    path = tmp_path / "plan.dxf"
    assert _build_demo_dxf(str(path), "en")
    texts = _texts(path)

    rooms = {re.sub(r"\s+[\d.]+ x [\d.]+$", "", t) for t in texts if " x " in t}
    assert {"Drawing Room", "Lounge", "Kitchen", "Bedroom", "Bath", "Store", "Porch", "Car Porch", "Lawn", "Staircase"} <= rooms
    german = re.compile(r"Wohnen|Schlafen|Küche|Bad\b|Flur|Grundriss|Erdgeschoss|,\d\d")
    assert not [t for t in texts if german.search(t)], texts
    # Every size label is "<name> <width> x <depth>" in metres with a decimal point.
    for t in texts:
        if " x " in t:
            assert re.search(r"\d\.\d\d x \d\.\d\d$", t), t


def test_german_plan_is_still_a_grundriss(tmp_path) -> None:
    path = tmp_path / "plan.dxf"
    assert _build_demo_dxf(str(path), "de")
    names = {t.split(" ")[0] for t in _texts(path)}
    assert names == {"Wohnen", "Schlafen"}
