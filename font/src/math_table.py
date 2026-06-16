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
    "DelimitedSubFormulaMinHeight": 10 * PIXEL,
    "DisplayOperatorMinHeight": 8 * PIXEL,
    "RadicalDegreeBottomRaisePercent": 60,
}


def _make_constants() -> ot.MathConstants:
    mc = ot.MathConstants()
    for name, value in _SCALARS.items():
        setattr(mc, name, int(value))
    for name, value in _CONSTANTS.items():
        setattr(mc, name, _mv(value))
    return mc


def add_math_table(font: TTFont) -> None:
    math = newTable("MATH")
    math.table = ot.MATH()
    math.table.Version = 0x00010000
    math.table.MathConstants = _make_constants()
    # MathGlyphInfo / MathVariants are optional; start without them and add
    # stretchy/variant data in a later milestone.
    math.table.MathGlyphInfo = None
    math.table.MathVariants = None
    font["MATH"] = math
