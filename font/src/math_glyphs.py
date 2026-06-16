"""MinecrafTeX math-specific glyphs and the stretchy-construction spec.

This module supplies everything Monocraft does not: the radical (U+221A) and
n-ary product (U+220F), display-size big operators, and -- most importantly --
the *vertical size variants* and *glyph-assembly parts* that let delimiters,
integrals and radicals GROW to fit their content. That adaptive sizing is the
whole point of MinecrafTeX versus a plain pixel font.

Design conventions
------------------
* All pieces are pixel-art on the shared 5-wide grid (matching Monocraft).
* Stretchy delimiters are centred on the math axis (3.5 px) like the base glyph.
* Assembly uses zero connector overlap (`MinConnectorOverlap = 0`) so parts abut
  on whole-pixel boundaries -- the engine can only grow them in 1 px steps, which
  keeps every assembled size perfectly crisp.

The build script consumes `math_extra_glyphs()`; the MATH table builder consumes
`MATH_CONSTRUCTIONS`.
"""
from __future__ import annotations

from dataclasses import dataclass

from pixelfont import Glyph, PIXEL, AXIS_PX

# Variant heights (in pixels) generated for each stretchy delimiter, on top of
# the ~7 px base glyph. Odd heights keep the centre on the 3.5 px axis.
_VARIANT_HEIGHTS = [9, 11, 13]


@dataclass
class Construction:
    """Stretchy construction for one base symbol.

    `variants` are (glyph_name, advance_units) smallest->largest, INCLUDING the
    base glyph first. `parts` are assembly GlyphPartRecords bottom->top as
    (glyph_name, start_conn, end_conn, full_advance, is_extender).
    """
    codepoint: int
    base_name: str | None          # None -> resolve from cmap at build time
    base_advance: int
    variants: list[tuple[str, int]]
    parts: list[tuple[str, int, int, int, bool]]


_glyphs: list[Glyph] = []
_constructions: list[Construction] = []


def _g(name: str, rows: list[str], bottom_px: int,
       advance_px: int = 6, codepoint: int | None = None) -> Glyph:
    gl = Glyph(name=name, codepoint=codepoint, rows=rows,
               advance_px=advance_px, bottom_px=bottom_px)
    _glyphs.append(gl)
    return gl


def _centred_bottom(height_px: int) -> int:
    """bottom_px so a glyph of given height is centred on the 3.5 px axis."""
    return round((AXIS_PX + 0.5) - height_px / 2)


def _add_vertical_delimiter(key: str, codepoint: int, base_name: str,
                            base_height_px: int,
                            top: list[str], ext: str, bottom: list[str],
                            mid: list[str] | None = None) -> None:
    """Register size variants + an assembly for a vertically-stretchy symbol.

    Variant glyph i = top + ext*k (+ mid + ext*k) + bottom, sized to the target
    heights. Assembly parts are the caps plus the extender(s).
    """
    variants: list[tuple[str, int]] = [(base_name, base_height_px * PIXEL)]

    for h in _VARIANT_HEIGHTS:
        if mid is None:
            k = h - len(top) - len(bottom)
            rows = top + [ext] * k + bottom
        else:
            k2 = (h - len(top) - len(bottom) - len(mid)) // 2
            rows = top + [ext] * k2 + mid + [ext] * k2 + bottom
        name = f"{key}.v{h}"
        _g(name, rows, _centred_bottom(len(rows)))
        variants.append((name, len(rows) * PIXEL))

    # Assembly parts (drawn at baseline; engine stacks + centres them).
    bot_name = f"{key}.bot"
    ext_name = f"{key}.ext"
    top_name = f"{key}.top"
    _g(bot_name, bottom, 0)
    _g(ext_name, [ext], 0)
    _g(top_name, top, 0)

    if mid is None:
        parts = [
            (bot_name, 0, 0, len(bottom) * PIXEL, False),
            (ext_name, 0, 0, PIXEL, True),
            (top_name, 0, 0, len(top) * PIXEL, False),
        ]
    else:
        mid_name = f"{key}.mid"
        _g(mid_name, mid, 0)
        parts = [
            (bot_name, 0, 0, len(bottom) * PIXEL, False),
            (ext_name, 0, 0, PIXEL, True),
            (mid_name, 0, 0, len(mid) * PIXEL, False),
            (ext_name, 0, 0, PIXEL, True),
            (top_name, 0, 0, len(top) * PIXEL, False),
        ]

    _constructions.append(Construction(codepoint, base_name,
                                       base_height_px * PIXEL, variants, parts))


# --- Stretchy delimiters (base glyphs come from Monocraft via cmap) ----------

_add_vertical_delimiter(
    "parenleft", 0x0028, "left_parenthesis", 7,
    top=["...#.", "..#..", ".#..."], ext=".#...",
    bottom=[".#...", "..#..", "...#."])

_add_vertical_delimiter(
    "parenright", 0x0029, "right_parenthesis", 7,
    top=[".#...", "..#..", "...#."], ext="...#.",
    bottom=["...#.", "..#..", ".#..."])

_add_vertical_delimiter(
    "bracketleft", 0x005B, "left_square_bracket", 7,
    top=[".###.", ".#..."], ext=".#...",
    bottom=[".#...", ".###."])

_add_vertical_delimiter(
    "bracketright", 0x005D, "right_square_bracket", 7,
    top=[".###.", "...#."], ext="...#.",
    bottom=["...#.", ".###."])

_add_vertical_delimiter(
    "braceleft", 0x007B, "left_curly_brace", 7,
    top=["...#.", "..#..", "..#.."], ext="..#..",
    mid=["##..."], bottom=["..#..", "..#..", "...#."])

_add_vertical_delimiter(
    "braceright", 0x007D, "right_curly_brace", 7,
    top=[".#...", "..#..", "..#.."], ext="..#..",
    mid=["...##"], bottom=["..#..", "..#..", ".#..."])

_add_vertical_delimiter(
    "bar", 0x007C, "vertical_line", 7,
    top=["..#.."], ext="..#..", bottom=["..#.."])


# --- Radical (Monocraft has no U+221A): base + upward-growing variants -------

_RAD_CHECK = ["#...#", ".#.#.", "..#.."]   # the V, bottom 3 rows
_RAD_VBAR = "....#"                          # rising right stroke


def _radical_rows(height_px: int) -> list[str]:
    return [_RAD_VBAR] * (height_px - len(_RAD_CHECK)) + _RAD_CHECK


# Base radical (7 px), sits on the baseline (grows upward, not axis-centred).
# Advance = 5 px so the engine-drawn vinculum starts exactly at the rising
# stroke (column 4); a 6 px advance would leave a 1 px gap in the overbar.
_g("radical", _radical_rows(7), 0, advance_px=5, codepoint=0x221A)
_rad_variants = [("radical", 7 * PIXEL)]
for h in _VARIANT_HEIGHTS:
    nm = f"radical.v{h}"
    _g(nm, _radical_rows(h), 0, advance_px=5)
    _rad_variants.append((nm, h * PIXEL))

# Radical assembly: check at the bottom, repeatable vertical stroke, top cap.
_g("radical.bot", _RAD_CHECK, 0, advance_px=5)
_g("radical.ext", [_RAD_VBAR], 0, advance_px=5)
_g("radical.top", [_RAD_VBAR], 0, advance_px=5)
_constructions.append(Construction(
    0x221A, "radical", 7 * PIXEL, _rad_variants,
    [("radical.bot", 0, 0, len(_RAD_CHECK) * PIXEL, False),
     ("radical.ext", 0, 0, PIXEL, True),
     ("radical.top", 0, 0, PIXEL, False)]))


# --- Display-size big operators ---------------------------------------------
# Base integral/sum come from Monocraft; we add a larger DISPLAY variant so they
# grow in display style (engine compares advance to DisplayOperatorMinHeight).

# Display integral: a taller S (12 px), centred low like the 8 px base.
_g("integral.display", [
    "...##",
    "..#.#",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "#.#..",
    "##...",
], bottom_px=-2, codepoint=None)
_constructions.append(Construction(
    0x222B, "integral", 8 * PIXEL,
    [("integral", 8 * PIXEL), ("integral.display", 12 * PIXEL)], []))

# Display summation (9 px tall sigma; vertex at the left-centre like the base).
_g("summation.display", [
    "#########",
    "#........",
    ".#.......",
    "..#......",
    "...#.....",
    "..#......",
    ".#.......",
    "#........",
    "#########",
], bottom_px=-1, advance_px=10, codepoint=None)
_constructions.append(Construction(
    0x2211, "n_ary_summation", 7 * PIXEL,
    [("n_ary_summation", 7 * PIXEL), ("summation.display", 9 * PIXEL)], []))

# N-ary product (Monocraft lacks U+220F): base + display variant.
_g("product", [
    "#####",
    ".#.#.",
    ".#.#.",
    ".#.#.",
    ".#.#.",
    ".#.#.",
    ".#.#.",
], bottom_px=0, codepoint=0x220F)
_g("product.display", [
    "#######",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
], bottom_px=-1, advance_px=8, codepoint=None)
_constructions.append(Construction(
    0x220F, "product", 7 * PIXEL,
    [("product", 7 * PIXEL), ("product.display", 9 * PIXEL)], []))


def math_extra_glyphs() -> list[Glyph]:
    """All MinecrafTeX-specific outline glyphs (radical, variants, parts, ...)."""
    return list(_glyphs)


MATH_CONSTRUCTIONS: list[Construction] = _constructions

# Italic corrections (units) so scripts on slanted/asymmetric operators clear the
# glyph body -- most important for the integral, whose limits sit at its side.
ITALIC_CORRECTIONS: dict[str, int] = {
    "integral": 2 * PIXEL,
    "integral.display": 3 * PIXEL,
}
