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

_LATIN_MATH_PLANES = [
    (0x1D400, 0x1D41A),  # bold
    (0x1D434, 0x1D44E),  # italic/default variables
    (0x1D468, 0x1D482),  # bold italic
    (0x1D49C, 0x1D4B6),  # script
    (0x1D4D0, 0x1D4EA),  # bold script
    (0x1D504, 0x1D51E),  # fraktur
    (0x1D538, 0x1D552),  # double-struck
    (0x1D56C, 0x1D586),  # bold fraktur
    (0x1D5A0, 0x1D5BA),  # sans-serif
    (0x1D5D4, 0x1D5EE),  # sans-serif bold
    (0x1D608, 0x1D622),  # sans-serif italic
    (0x1D63C, 0x1D656),  # sans-serif bold italic
    (0x1D670, 0x1D68A),  # monospace
]


def _galactic_feature(font: TTFont) -> str:
    cmap = font.getBestCmap()
    lines: list[str] = []
    seen_sources: set[str] = set()

    def add(source: str | None, target: str | None) -> None:
        if source is None or target is None or source in seen_sources:
            return
        seen_sources.add(source)
        lines.append(f"    sub {source} by {target};")

    for index, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
        target = cmap.get(_GALACTIC_BASE + index)
        if target is None:
            continue
        add(cmap.get(ord(letter)), target)
        add(cmap.get(ord(letter.upper())), target)
        for cap_start, small_start in _LATIN_MATH_PLANES:
            add(cmap.get(cap_start + index), target)
            add(cmap.get(small_start + index), target)
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
