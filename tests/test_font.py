"""Pytest checks for the built MinecrafTeX font (run after build_font.py)."""
import os
import subprocess
import sys

import pytest
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTF = os.path.join(ROOT, "font", "dist", "MinecrafTeX-Math.ttf")


@pytest.fixture(scope="module")
def font():
    if not os.path.exists(TTF):
        subprocess.run([sys.executable, os.path.join(ROOT, "font", "build_font.py")],
                       check=True)
    return TTFont(TTF)


def test_has_math_table(font):
    assert "MATH" in font


def test_math_constants_pixel_snapped(font):
    mc = font["MATH"].table.MathConstants
    # Every MathValueRecord must be a whole number of pixels (100 units).
    assert mc.FractionRuleThickness.Value == 100
    assert mc.AxisHeight.Value % 100 == 0
    assert mc.RadicalRuleThickness.Value == 100


def test_core_glyphs_present(font):
    cmap = font.getBestCmap()
    for cp in (0x0030, 0x0031, 0x0078, 0x006E, 0x003D,
               0x222B, 0x2211, 0x221A, 0x2212):
        assert cp in cmap, f"missing U+{cp:04X}"


def test_roundtrip(tmp_path, font):
    out = tmp_path / "rt.ttf"
    font.save(str(out))
    again = TTFont(str(out))
    assert again["MATH"].table.MathConstants.FractionRuleThickness.Value == 100
