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
    # Most MathValueRecords are whole pixels (100 units).
    assert mc.FractionRuleThickness.Value == 100
    assert mc.RadicalRuleThickness.Value == 100
    # The math axis is snapped to the HALF-pixel grid (350 = 3.5 px): Monocraft's
    # +, -, = operators centre on y=3.5 px, so the axis must too, otherwise the
    # engine half-pixel-shifts every stretchy delimiter. Allow any 0.5 px step.
    assert mc.AxisHeight.Value % 50 == 0


def test_core_glyphs_present(font):
    cmap = font.getBestCmap()
    for cp in (0x0030, 0x0031, 0x0078, 0x006E, 0x003D,
               0x222B, 0x2211, 0x221A, 0x2212):
        assert cp in cmap, f"missing U+{cp:04X}"


def test_added_relation_glyphs_present(font):
    """Common relations/operators Monocraft lacks are now drawn as pixels."""
    cmap = font.getBestCmap()
    for cp in (0x2264, 0x2265, 0x2248, 0x223C, 0x2208, 0x220B,
               0x2207, 0x22C5, 0x222A, 0x2205):
        assert cp in cmap, f"missing U+{cp:04X}"


def test_math_alphanumeric_aliased(font):
    """Math italic/bold letters (and italic phi) must map to pixel glyphs so
    unicode-math does not fall back to Latin Modern serif."""
    cmap = font.getBestCmap()
    for cp in (0x1D465,  # math italic x
               0x1D400,  # math bold A
               0x1D719,  # math italic phi symbol -> phi
               0x1D6FC,  # math italic alpha
               0x1D7CE): # math bold digit 0
        assert cp in cmap, f"missing U+{cp:04X}"


def test_roundtrip(tmp_path, font):
    out = tmp_path / "rt.ttf"
    font.save(str(out))
    again = TTFont(str(out))
    assert again["MATH"].table.MathConstants.FractionRuleThickness.Value == 100


def test_math_script_present(font):
    """A `math` script tag in GSUB stops unicode-math's Latin Modern fallback."""
    scripts = font["GSUB"].table.ScriptList.ScriptRecord
    assert any(s.ScriptTag == "math" for s in scripts)


def test_math_variants_stretchy(font):
    """Stretchy delimiters/operators must expose vertical size variants."""
    mv = font["MATH"].table.MathVariants
    assert mv is not None
    assert mv.VertGlyphCount > 0
    covered = set(mv.VertGlyphCoverage.glyphs)
    order = font.getGlyphOrder()
    for name in ("left_parenthesis", "right_parenthesis", "left_curly_brace",
                 "radical", "integral", "n_ary_summation"):
        assert name in order, f"missing glyph {name}"
        assert name in covered, f"{name} has no vertical variants"
    # Each construction lists at least the base plus one larger variant.
    for c in mv.VertGlyphConstruction:
        assert c.VariantCount >= 1


def test_integral_italic_correction(font):
    """Integral needs italic correction so display limits clear the glyph."""
    info = font["MATH"].table.MathGlyphInfo
    assert info is not None and info.MathItalicsCorrectionInfo is not None
    ic = info.MathItalicsCorrectionInfo
    assert "integral" in set(ic.Coverage.glyphs)


def test_integral_subscript_kern(font):
    """Integral carries a bottom-right cut-in kern so its lower limit tucks
    clear of the hook (the MathKernInfo path, not just italic correction)."""
    info = font["MATH"].table.MathGlyphInfo
    assert info is not None and info.MathKernInfo is not None
    ki = info.MathKernInfo
    covered = set(ki.MathKernCoverage.glyphs)
    assert "integral" in covered
    idx = ki.MathKernCoverage.glyphs.index("integral")
    rec = ki.MathKernInfoRecords[idx]
    assert rec.BottomRightMathKern is not None
    assert rec.BottomRightMathKern.KernValue[0].Value > 0

