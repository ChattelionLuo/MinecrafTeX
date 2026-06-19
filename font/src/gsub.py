"""Add MinecrafTeX GSUB features.

unicode-math decides whether a font is a "real" math font with a single gate:
`\fontspec_if_script:nF {math}` -- it checks the font's GSUB/GPOS ScriptList for
a script tagged `math`. If absent, it silently loads latinmodern-math.otf over
the top, so every symbol renders in Latin Modern instead of our pixels.

We therefore attach a minimal `ssty` lookup under the `math` script. We also add
an `ss01` stylistic set that maps ASCII letters to Monocraft's Standard Galactic
Alphabet PUA glyphs when requested by LaTeX or CSS.
"""
from __future__ import annotations

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont


_GALACTIC_BASE = 0xEB40


def _galactic_feature(font: TTFont) -> str:
    cmap = font.getBestCmap()
    lines: list[str] = []
    for index, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
        target = cmap.get(_GALACTIC_BASE + index)
        lower = cmap.get(ord(letter))
        upper = cmap.get(ord(letter.upper()))
        if target is None:
            continue
        if lower is not None:
            lines.append(f"    sub {lower} by {target};")
        if upper is not None:
            lines.append(f"    sub {upper} by {target};")
    if not lines:
        return ""
    return "feature ss01 {\n" + "\n".join(lines) + "\n} ss01;\n"


def add_math_script(font: TTFont, anchor_glyph: str) -> None:
    """Register the `math` script in GSUB so unicode-math accepts the font.

    `anchor_glyph` must be an existing glyph name; we map it to itself.
    """
    fea = (
        "languagesystem DFLT dflt;\n"
        "languagesystem latn dflt;\n"
        "languagesystem math dflt;\n"
        + _galactic_feature(font) +
        "feature ssty {\n"
        "    script math;\n"
        "    language dflt;\n"
        f"    sub {anchor_glyph} by {anchor_glyph};\n"
        "} ssty;\n"
    )
    addOpenTypeFeaturesFromString(font, fea)
