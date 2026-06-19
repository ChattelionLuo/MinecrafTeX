"""Generate styled Mathematical Alphanumeric glyphs from base pixels.

Regular MinecrafTeX aliases ordinary math italic codepoints back to upright
pixel glyphs, because unicode-math uses those codepoints for default variables.
This module creates transformed glyphs only for explicit bold and bold-italic
math alphabets while keeping the rest of the alias machinery in
``math_alphanum.py``.
"""
from __future__ import annotations

from pixelfont import Glyph

LATIN_UPPER = list(range(ord("A"), ord("Z") + 1))
LATIN_LOWER = list(range(ord("a"), ord("z") + 1))
DIGITS = list(range(ord("0"), ord("9") + 1))

GREEK_CAP_ORDER = (
    list(range(0x391, 0x3A2)) + [0x398] + list(range(0x3A3, 0x3AA)) + [0x2207]
)
GREEK_SMALL_ORDER = (
    list(range(0x3B1, 0x3CA)) + [0x2202, 0x3B5, 0x3B8, 0x3BA, 0x3C6, 0x3C1, 0x3C0]
)

STYLE_PLANES = [
    ("bold", 0x1D400, 0x1D41A, 0x1D6A8, 0x1D6C2, 0x1D7CE, 0.2, 0.0),
    ("bolditalic", 0x1D468, 0x1D482, 0x1D71C, 0x1D736, None, 0.2, 15.0),
]


def _copy_glyph(base: Glyph, *, name: str, codepoint: int,
                embolden_px: float, slant_degrees: float) -> Glyph:
    return Glyph(
        name=name,
        codepoint=codepoint,
        rows=list(base.rows),
        advance_px=base.advance_px,
        x_offset_px=base.x_offset_px,
        embolden_px=base.embolden_px + embolden_px,
        slant_degrees=base.slant_degrees + slant_degrees,
        bottom_px=base.bottom_px,
    )


def styled_math_glyphs(glyph_by_cp: dict[int, Glyph]) -> list[Glyph]:
    out: list[Glyph] = []
    seen: set[int] = set()

    def add(cp: int, base_cp: int, style: str, embolden_px: float,
            slant_degrees: float) -> None:
        if cp in seen:
            return
        base = glyph_by_cp.get(base_cp)
        if base is None:
            return
        out.append(_copy_glyph(
            base,
            name=f"{base.name}.{style}.math.{cp:04X}",
            codepoint=cp,
            embolden_px=embolden_px,
            slant_degrees=slant_degrees,
        ))
        seen.add(cp)

    for style, cap_start, small_start, greek_cap_start, greek_small_start, digit_start, embolden, slant in STYLE_PLANES:
        for index, base_cp in enumerate(LATIN_UPPER):
            add(cap_start + index, base_cp, style, embolden, slant)
        for index, base_cp in enumerate(LATIN_LOWER):
            add(small_start + index, base_cp, style, embolden, slant)
        for index, base_cp in enumerate(GREEK_CAP_ORDER):
            add(greek_cap_start + index, base_cp, style, embolden, slant)
        for index, base_cp in enumerate(GREEK_SMALL_ORDER):
            add(greek_small_start + index, base_cp, style, embolden, slant)
        if digit_start is not None:
            for index, base_cp in enumerate(DIGITS):
                add(digit_start + index, base_cp, style, embolden, slant)

    return out
