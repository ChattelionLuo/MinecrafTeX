"""Builds the OpenType MATH table for MinecrafTeX.

The MATH table is what teaches a math engine (unicode-math, or a browser's
MathML renderer) how to lay out fractions, radicals, scripts and big operators.
Every value here is a whole multiple of one pixel (PIXEL=100 units) so that bars
and gaps always land on pixel boundaries and stay crisp.
"""
from __future__ import annotations

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables as ot

from pixelfont import PIXEL, AXIS_HEIGHT, CAP_HEIGHT
from math_glyphs import MATH_CONSTRUCTIONS, ITALIC_CORRECTIONS, MATH_KERNS


def _mv(value: int) -> ot.MathValueRecord:
    rec = ot.MathValueRecord()
    rec.Value = int(value)
    rec.DeviceTable = None
    return rec


# name -> value. MathValueRecord fields use _mv(); the four percent/height
# scalars at the boundaries are plain ints (handled below).
_CONSTANTS = {
    "MathLeading": 1 * PIXEL,
    "AxisHeight": AXIS_HEIGHT,
    "AccentBaseHeight": CAP_HEIGHT,
    "FlattenedAccentBaseHeight": CAP_HEIGHT,
    "SubscriptShiftDown": 1 * PIXEL,
    "SubscriptTopMax": 4 * PIXEL,
    "SubscriptBaselineDropMin": 1 * PIXEL,
    "SuperscriptShiftUp": 3 * PIXEL,
    "SuperscriptShiftUpCramped": 2 * PIXEL,
    "SuperscriptBottomMin": 1 * PIXEL,
    "SuperscriptBaselineDropMax": 3 * PIXEL,
    "SubSuperscriptGapMin": 1 * PIXEL,
    "SuperscriptBottomMaxWithSubscript": 4 * PIXEL,
    "SpaceAfterScript": 1 * PIXEL,
    "UpperLimitGapMin": 1 * PIXEL,
    "UpperLimitBaselineRiseMin": 1 * PIXEL,
    "LowerLimitGapMin": 1 * PIXEL,
    "LowerLimitBaselineDropMin": 1 * PIXEL,
    "StackTopShiftUp": 3 * PIXEL,
    "StackTopDisplayStyleShiftUp": 4 * PIXEL,
    "StackBottomShiftDown": 3 * PIXEL,
    "StackBottomDisplayStyleShiftDown": 4 * PIXEL,
    "StackGapMin": 1 * PIXEL,
    "StackDisplayStyleGapMin": 2 * PIXEL,
    "StretchStackTopShiftUp": 3 * PIXEL,
    "StretchStackBottomShiftDown": 3 * PIXEL,
    "StretchStackGapAboveMin": 1 * PIXEL,
    "StretchStackGapBelowMin": 1 * PIXEL,
    "FractionNumeratorShiftUp": 4 * PIXEL,
    "FractionNumeratorDisplayStyleShiftUp": 5 * PIXEL,
    "FractionDenominatorShiftDown": 4 * PIXEL,
    "FractionDenominatorDisplayStyleShiftDown": 5 * PIXEL,
    "FractionNumeratorGapMin": 1 * PIXEL,
    "FractionNumDisplayStyleGapMin": 1 * PIXEL,
    "FractionRuleThickness": 1 * PIXEL,
    "FractionDenominatorGapMin": 1 * PIXEL,
    "FractionDenomDisplayStyleGapMin": 1 * PIXEL,
    "SkewedFractionHorizontalGap": 1 * PIXEL,
    "SkewedFractionVerticalGap": 1 * PIXEL,
    "OverbarVerticalGap": 1 * PIXEL,
    "OverbarRuleThickness": 1 * PIXEL,
    "OverbarExtraAscender": 1 * PIXEL,
    "UnderbarVerticalGap": 1 * PIXEL,
    "UnderbarRuleThickness": 1 * PIXEL,
    "UnderbarExtraDescender": 1 * PIXEL,
    "RadicalVerticalGap": 1 * PIXEL,
    "RadicalDisplayStyleVerticalGap": 1 * PIXEL,
    "RadicalRuleThickness": 1 * PIXEL,
    "RadicalExtraAscender": 1 * PIXEL,
    "RadicalKernBeforeDegree": 1 * PIXEL,
    "RadicalKernAfterDegree": -1 * PIXEL,
}

# plain-integer (non MathValueRecord) constants
_SCALARS = {
    "ScriptPercentScaleDown": 70,
    "ScriptScriptPercentScaleDown": 50,
    # Let \left|x\right| and \left(x\right) use the hand-balanced base glyphs;
    # taller contents still trigger the pre-drawn variants or assemblies.
    "DelimitedSubFormulaMinHeight": 7 * PIXEL,
    "DisplayOperatorMinHeight": 9 * PIXEL,
    "RadicalDegreeBottomRaisePercent": 60,
}


def _make_constants() -> ot.MathConstants:
    mc = ot.MathConstants()
    for name, value in _SCALARS.items():
        setattr(mc, name, int(value))
    for name, value in _CONSTANTS.items():
        setattr(mc, name, _mv(value))
    return mc


def _variant_record(glyph_name: str, advance: int) -> ot.MathGlyphVariantRecord:
    rec = ot.MathGlyphVariantRecord()
    rec.VariantGlyph = glyph_name
    rec.AdvanceMeasurement = int(advance)
    return rec


def _part_record(glyph_name: str, start: int, end: int,
                 full: int, extender: bool) -> ot.GlyphPartRecord:
    rec = ot.GlyphPartRecord()
    rec.glyph = glyph_name
    rec.StartConnectorLength = int(start)
    rec.EndConnectorLength = int(end)
    rec.FullAdvance = int(full)
    rec.PartFlags = 0x0001 if extender else 0x0000
    return rec


def _make_construction(con, base_name: str) -> ot.MathGlyphConstruction:
    gc = ot.MathGlyphConstruction()
    variants = [(base_name, con.base_advance)] + con.variants[1:]
    gc.VariantCount = len(variants)
    gc.MathGlyphVariantRecord = [_variant_record(n, a) for n, a in variants]
    if con.parts:
        ga = ot.GlyphAssembly()
        ga.ItalicsCorrection = _mv(0)
        ga.PartCount = len(con.parts)
        ga.PartRecords = [_part_record(*p) for p in con.parts]
        gc.GlyphAssembly = ga
    else:
        gc.GlyphAssembly = None
    return gc


def _make_variants(font: TTFont) -> ot.MathVariants:
    """Build MathVariants from MATH_CONSTRUCTIONS, aligned to glyph-ID order."""
    cmap = font.getBestCmap()
    gid = {name: i for i, name in enumerate(font.getGlyphOrder())}

    resolved = []  # (gid, base_name, construction)
    for con in MATH_CONSTRUCTIONS:
        base_name = cmap.get(con.codepoint, con.base_name)
        if base_name is None or base_name not in gid:
            continue
        resolved.append((gid[base_name], base_name, con))
    resolved.sort(key=lambda t: t[0])  # coverage MUST be in GID order

    mv = ot.MathVariants()
    mv.MinConnectorOverlap = 0  # parts abut on whole-pixel boundaries
    cov = ot.Coverage()
    cov.glyphs = [base_name for _, base_name, _ in resolved]
    mv.VertGlyphCoverage = cov
    mv.VertGlyphCount = len(resolved)
    mv.VertGlyphConstruction = [
        _make_construction(con, base_name) for _, base_name, con in resolved
    ]
    horiz = ot.Coverage()
    horiz.glyphs = []
    mv.HorizGlyphCoverage = horiz
    mv.HorizGlyphCount = 0
    mv.HorizGlyphConstruction = []
    return mv


def _make_kern(value: int) -> ot.MathKern:
    """A flat math kern (no height steps): one correction applied at all heights."""
    k = ot.MathKern()
    k.HeightCount = 0
    k.CorrectionHeight = []
    k.KernValue = [_mv(value)]
    return k


def _make_kern_info(font: TTFont) -> ot.MathKernInfo | None:
    """Per-corner cut-in kerns so big-operator limits clear the glyph hooks."""
    gid = {name: i for i, name in enumerate(font.getGlyphOrder())}
    items = [(gid[n], n, c) for n, c in MATH_KERNS.items() if n in gid]
    if not items:
        return None
    items.sort(key=lambda t: t[0])  # coverage in GID order

    ki = ot.MathKernInfo()
    cov = ot.Coverage()
    cov.glyphs = [n for _, n, _ in items]
    ki.MathKernCoverage = cov
    ki.MathKernCount = len(items)
    records = []
    for _, _, corners in items:
        rec = ot.MathKernInfoRecord()
        rec.TopRightMathKern = _make_kern(corners["tr"]) if "tr" in corners else None
        rec.TopLeftMathKern = _make_kern(corners["tl"]) if "tl" in corners else None
        rec.BottomRightMathKern = _make_kern(corners["br"]) if "br" in corners else None
        rec.BottomLeftMathKern = _make_kern(corners["bl"]) if "bl" in corners else None
        records.append(rec)
    ki.MathKernInfoRecords = records
    return ki


def _make_glyph_info(font: TTFont) -> ot.MathGlyphInfo | None:
    """Italic corrections so operator limits/scripts clear the glyph body."""
    gid = {name: i for i, name in enumerate(font.getGlyphOrder())}
    items = [(gid[n], n, v) for n, v in ITALIC_CORRECTIONS.items() if n in gid]
    kern_info = _make_kern_info(font)
    if not items and kern_info is None:
        return None
    items.sort(key=lambda t: t[0])  # coverage in GID order

    ic = ot.MathItalicsCorrectionInfo()
    cov = ot.Coverage()
    cov.glyphs = [n for _, n, _ in items]
    ic.Coverage = cov
    ic.ItalicsCorrectionCount = len(items)
    ic.ItalicsCorrection = [_mv(v) for _, _, v in items]

    info = ot.MathGlyphInfo()
    info.MathItalicsCorrectionInfo = ic
    info.MathTopAccentAttachment = None
    info.ExtendedShapeCoverage = None
    info.MathKernInfo = kern_info
    return info


def add_math_table(font: TTFont) -> None:
    math = newTable("MATH")
    math.table = ot.MATH()
    math.table.Version = 0x00010000
    math.table.MathConstants = _make_constants()
    math.table.MathGlyphInfo = _make_glyph_info(font)
    math.table.MathVariants = _make_variants(font)
    font["MATH"] = math
