"""Add a GSUB table carrying the OpenType `math` script.

unicode-math decides whether a font is a "real" math font with a single gate:
`\fontspec_if_script:nF {math}` -- it checks the font's GSUB/GPOS ScriptList for
a script tagged `math`. If absent, it silently loads latinmodern-math.otf over
the top, so every symbol renders in Latin Modern instead of our pixels.

We therefore attach a minimal GSUB containing the `math` (and `DFLT`) scripts
and one harmless `ssty` lookup (a single-substitution self-map). The lookup does
nothing visible; its only job is to make the `math` script present and valid.
"""
from __future__ import annotations

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont


def add_math_script(font: TTFont, anchor_glyph: str) -> None:
    """Register the `math` script in GSUB so unicode-math accepts the font.

    `anchor_glyph` must be an existing glyph name; we map it to itself.
    """
    fea = (
        "languagesystem DFLT dflt;\n"
        "languagesystem math dflt;\n"
        "feature ssty {\n"
        "    script math;\n"
        "    language dflt;\n"
        f"    sub {anchor_glyph} by {anchor_glyph};\n"
        "} ssty;\n"
    )
    addOpenTypeFeaturesFromString(font, fea)
