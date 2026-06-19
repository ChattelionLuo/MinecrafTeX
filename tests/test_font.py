"""Pytest checks for the built MinecrafTeX font (run after build_font.py)."""
import os
import subprocess
import sys

import pytest
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTF = os.path.join(ROOT, "font", "dist", "MinecrafTeX-Math.ttf")
PROP_TTF = os.path.join(ROOT, "font", "dist", "MinecrafTeX-Math-Proportional.ttf")
PROP_BOLD_TTF = os.path.join(ROOT, "font", "dist", "MinecrafTeX-Math-Proportional-Bold.ttf")
PROP_ITALIC_TTF = os.path.join(ROOT, "font", "dist", "MinecrafTeX-Math-Proportional-Italic.ttf")


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
    # Simple \left|x\right| should not be forced up to a tall variant; the base
    # delimiter glyphs are hand-lowered to balance x-height content.
    assert mc.DelimitedSubFormulaMinHeight == 700


def test_core_glyphs_present(font):
    cmap = font.getBestCmap()
    for cp in (0x0030, 0x0031, 0x0078, 0x006E, 0x003D,
               0x222B, 0x2211, 0x221A, 0x2212):
        assert cp in cmap, f"missing U+{cp:04X}"


def test_narrow_math_marks_have_tight_advances(font):
    """Prime-like marks and bars should not keep the full monospace advance."""
    cmap = font.getBestCmap()
    hmtx = font["hmtx"].metrics
    expected = {
        0x0027: 300,  # apostrophe
        0x007C: 400,  # vertical bar
        0x2032: 300,  # prime
        0x2033: 400,  # double prime
    }
    for cp, advance in expected.items():
        assert cp in cmap, f"missing U+{cp:04X}"
        assert hmtx[cmap[cp]][0] == advance


def test_narrow_marks_are_optically_centered(font):
    """Tight punctuation should not be left-pinned inside its narrower advance."""
    cmap = font.getBestCmap()
    glyf = font["glyf"]
    hmtx = font["hmtx"].metrics
    for cp in (0x007C, 0x0027):
        name = cmap[cp]
        advance = hmtx[name][0]
        glyph = glyf[name]
        left_gap = glyph.xMin
        right_gap = advance - glyph.xMax
        assert abs(left_gap - right_gap) <= 50


def test_proportional_font_has_natural_text_metrics():
    if not os.path.exists(PROP_TTF):
        subprocess.run([sys.executable, os.path.join(ROOT, "font", "build_font.py")],
                       check=True)
    font = TTFont(PROP_TTF)
    cmap = font.getBestCmap()
    hmtx = font["hmtx"].metrics
    assert hmtx[cmap[ord("A")]][0] == 600
    assert hmtx[cmap[ord("i")]][0] < hmtx[cmap[ord("A")]][0]
    assert hmtx[cmap[ord("i")]][1] == 50


def test_proportional_text_style_fonts_present():
    if not os.path.exists(PROP_BOLD_TTF) or not os.path.exists(PROP_ITALIC_TTF):
        subprocess.run([sys.executable, os.path.join(ROOT, "font", "build_font.py")],
                       check=True)
    bold = TTFont(PROP_BOLD_TTF)
    italic = TTFont(PROP_ITALIC_TTF)
    assert bold["OS/2"].usWeightClass == 700
    assert bold["head"].macStyle & 0x01
    assert italic["post"].italicAngle == -15
    assert italic["head"].macStyle & 0x02


def test_default_math_is_upright_but_bold_variants_are_real(font):
    cmap = font.getBestCmap()
    glyf = font["glyf"]
    plain_x = cmap[ord("x")]
    bold_x = cmap[0x1D431]  # MATHEMATICAL BOLD SMALL X
    italic_x = cmap[0x1D465]  # MATHEMATICAL ITALIC SMALL X, used for default x
    bolditalic_x = cmap[0x1D499]  # MATHEMATICAL BOLD ITALIC SMALL X
    assert bold_x != plain_x
    assert italic_x == plain_x
    assert bolditalic_x != plain_x
    assert glyf[bold_x].xMin < glyf[plain_x].xMin
    assert glyf[bolditalic_x].xMax > glyf[plain_x].xMax


def test_added_relation_glyphs_present(font):
    """Common relations/operators Monocraft lacks are now drawn as pixels."""
    cmap = font.getBestCmap()
    for cp in (0x2264, 0x2265, 0x2248, 0x223C, 0x2208, 0x220B,
               0x2207, 0x22C5, 0x222A, 0x2205):
        assert cp in cmap, f"missing U+{cp:04X}"


def test_math_alphanumeric_aliased(font):
    """Math alphabet letters (including default italic variables) must map so
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


def test_tall_square_bracket_variant_available(font):
    """Tall matrices should use a solid right bracket before assembly fallback."""
    mv = font["MATH"].table.MathVariants
    idx = mv.VertGlyphCoverage.glyphs.index("right_square_bracket")
    variants = mv.VertGlyphConstruction[idx].MathGlyphVariantRecord
    assert max(v.AdvanceMeasurement for v in variants) >= 10100


def test_radical_connector_aligns_with_vinculum(font):
    """The radical connector should overlap the overbar on the same pixel row."""
    mc = font["MATH"].table.MathConstants
    assert mc.RadicalExtraAscender.Value == 0
    glyf = font["glyf"]
    hmtx = font["hmtx"].metrics
    for name in ("radical", "radical.v9", "radical.v25"):
        assert glyf[name].xMax >= hmtx[name][0] + 100


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

