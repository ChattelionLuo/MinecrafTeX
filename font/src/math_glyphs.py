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
# the ~7 px base glyph. ODD heights stay centred on the 3.5 px math axis, so the
# engine never has to half-pixel-shift them. We pre-draw a generous range so that
# realistic content (fractions, nested fractions) always hits a crisp solid
# variant and only pathologically tall content falls back to glyph assembly.
_VARIANT_HEIGHTS = [9, 11, 13, 15, 17, 19, 21, 23, 25,
                    31, 37, 43, 51, 61, 73, 87, 101]


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
                            mid: list[str] | None = None,
                            advance_px: int = 5) -> None:
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
        _g(name, rows, _centred_bottom(len(rows)), advance_px=advance_px)
        variants.append((name, len(rows) * PIXEL))

    # Assembly parts (drawn at baseline; engine stacks + centres them). Each part
    # advertises a connector region equal to its full advance and the extender is
    # 1 px tall, so the engine can overlap neighbours on matching pixel columns to
    # hit any target height exactly -- no gaps between the caps and the extender.
    bot_name = f"{key}.bot"
    ext_name = f"{key}.ext"
    top_name = f"{key}.top"
    _g(bot_name, bottom, 0, advance_px=advance_px)
    _g(ext_name, [ext], 0, advance_px=advance_px)
    _g(top_name, top, 0, advance_px=advance_px)

    nb, nt = len(bottom) * PIXEL, len(top) * PIXEL
    if mid is None:
        parts = [
            (bot_name, 0, nb, nb, False),
            (ext_name, PIXEL, PIXEL, PIXEL, True),
            (top_name, nt, 0, nt, False),
        ]
    else:
        mid_name = f"{key}.mid"
        _g(mid_name, mid, 0, advance_px=advance_px)
        nm = len(mid) * PIXEL
        parts = [
            (bot_name, 0, nb, nb, False),
            (ext_name, PIXEL, PIXEL, PIXEL, True),
            (mid_name, nm, nm, nm, False),
            (ext_name, PIXEL, PIXEL, PIXEL, True),
            (top_name, nt, 0, nt, False),
        ]

    _constructions.append(Construction(codepoint, base_name,
                                       base_height_px * PIXEL, variants, parts))


# --- Stretchy delimiters (base glyphs come from Monocraft via cmap) ----------

_add_vertical_delimiter(
    "parenleft", 0x0028, "left_parenthesis", 7,
    top=["..##.", ".##..", ".#..."], ext=".#...",
    bottom=[".#...", ".##..", "..##."])

_add_vertical_delimiter(
    "parenright", 0x0029, "right_parenthesis", 7,
    top=[".##..", "..##.", "...#."], ext="...#.",
    bottom=["...#.", "..##.", ".##.."])

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
    top=["..##.", "..#..", "..#.."], ext="..#..",
    mid=[".#...", "#....", ".#..."], bottom=["..#..", "..#..", "..##."])

_add_vertical_delimiter(
    "braceright", 0x007D, "right_curly_brace", 7,
    top=[".##..", "..#..", "..#.."], ext="..#..",
    mid=["...#.", "....#", "...#."], bottom=["..#..", "..#..", ".##.."])

_add_vertical_delimiter(
    "bar", 0x007C, "vertical_line", 7,
    top=["..#.."], ext="..#..", bottom=["..#.."])


# --- Radical (Monocraft has no U+221A): base + upward-growing variants -------
#
# The surd has a 6 px advance. The top row draws 1 px past that advance so it
# overlaps TeX's vinculum; an exact edge-to-edge join can rasterize with a
# hairline seam in PDFs. MinecrafTeX sets RadicalExtraAscender to zero so this
# connector and the overbar occupy the same pixel row.
_RAD_CHECK = ["#...#.", ".#.#..", "..#..."]   # the V, bottom 3 rows (width 6)
_RAD_VBAR = "....#."                            # rising right stroke (col 4)
_RAD_TOP = "....###"                            # stroke + 1 px overbar overlap


def _radical_rows(height_px: int) -> list[str]:
    n_vbar = height_px - len(_RAD_CHECK) - 1
    return [_RAD_TOP] + [_RAD_VBAR] * n_vbar + _RAD_CHECK


# Base radical (7 px), sits on the baseline (grows upward, not axis-centred).
_g("radical", _radical_rows(7), 0, advance_px=6, codepoint=0x221A)
_rad_variants = [("radical", 7 * PIXEL)]
for h in _VARIANT_HEIGHTS:
    nm = f"radical.v{h}"
    _g(nm, _radical_rows(h), 0, advance_px=6)
    _rad_variants.append((nm, h * PIXEL))

# Radical assembly: check at the bottom, repeatable vertical stroke, top cap with
# the connecting tongue.
_g("radical.bot", _RAD_CHECK, 0, advance_px=6)
_g("radical.ext", [_RAD_VBAR], 0, advance_px=6)
_g("radical.top", [_RAD_TOP], 0, advance_px=6)
_constructions.append(Construction(
    0x221A, "radical", 7 * PIXEL, _rad_variants,
    [("radical.bot", 0, len(_RAD_CHECK) * PIXEL, len(_RAD_CHECK) * PIXEL, False),
     ("radical.ext", PIXEL, PIXEL, PIXEL, True),
    ("radical.top", PIXEL, 0, PIXEL, False)]))


# --- Display-size big operators ---------------------------------------------
# Base integral/sum come from Monocraft; we add a larger DISPLAY variant so they
# grow in display style (engine compares advance to DisplayOperatorMinHeight).

# Display integral: a tall, graceful S (15 px) so it visually spans a typical
# display integrand (a fraction/radical), matching Computer Modern's display
# integral. Big operators do NOT stretch to the integrand (that is not how TeX
# works); they have a single fixed display size, which is what this variant is.
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
    "..#..",
    "..#..",
    "..#..",
    "#.#..",
    "##...",
], bottom_px=-3, codepoint=None)
_constructions.append(Construction(
    0x222B, "integral", 8 * PIXEL,
    [("integral", 8 * PIXEL), ("integral.display", 15 * PIXEL)], []))

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


# --- Plain math symbols Monocraft is missing -------------------------------
# Common relations/operators absent from the base set. Drawn 7-row on the shared
# 5-wide grid (bottom_px = 0, like Monocraft operators) so they sit naturally in
# a line of pixel math.

_g("less_equal", [
    "...#.",
    "..#..",
    ".#...",
    "..#..",
    "...#.",
    ".....",
    "#####",
], bottom_px=0, codepoint=0x2264)

_g("greater_equal", [
    ".#...",
    "..#..",
    "...#.",
    "..#..",
    ".#...",
    ".....",
    "#####",
], bottom_px=0, codepoint=0x2265)

_g("approx_equal", [
    ".....",
    ".#.##",
    "##.#.",
    ".....",
    ".#.##",
    "##.#.",
    ".....",
], bottom_px=0, codepoint=0x2248)

_g("tilde_operator", [
    ".....",
    ".....",
    ".#..#",
    "#.#.#",
    "#..#.",
    ".....",
    ".....",
], bottom_px=0, codepoint=0x223C)

_g("element_of", [
    "..###",
    ".#...",
    "#....",
    "####.",
    "#....",
    ".#...",
    "..###",
], bottom_px=0, codepoint=0x2208)

_g("contains_member", [
    "###..",
    "...#.",
    "....#",
    ".####",
    "....#",
    "...#.",
    "###..",
], bottom_px=0, codepoint=0x220B)

_g("nabla", [
    "#####",
    "#...#",
    "#...#",
    ".#.#.",
    ".#.#.",
    "..#..",
    ".....",
], bottom_px=0, codepoint=0x2207)

_g("dot_operator", [
    ".....",
    ".....",
    ".....",
    "..#..",
    ".....",
    ".....",
    ".....",
], bottom_px=0, advance_px=4, codepoint=0x22C5)

_g("union", [
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    ".###.",
], bottom_px=0, codepoint=0x222A)

_g("empty_set", [
    "....#",
    ".###.",
    "#..##",
    "#.#.#",
    "##..#",
    ".###.",
    "#....",
], bottom_px=0, codepoint=0x2205)


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

# Math cut-in kerns (units) per glyph corner, so a big operator's limits tuck
# past its hooks instead of colliding with them -- the same mechanism real math
# fonts use for integral limits. Corners: 'tr','tl','br','bl'. Any corner left
# unset falls back to the italic correction. The integral's lower limit attaches
# at the bottom-right; a positive kern pushes it clear of the left-leaning hook.
MATH_KERNS: dict[str, dict[str, int]] = {
    "integral": {"br": 4 * PIXEL},
    "integral.display": {"br": 6 * PIXEL},
}
