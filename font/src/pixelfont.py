"""MinecrafTeX pixel-font core.

Turns ASCII pixel-art glyph definitions into a real OpenType font (TrueType
`glyf` outlines) using fontTools only -- no FontForge required, so the font can
be built on any machine with `pip install fonttools`.

Design grid
-----------
* UPM (units per em)      = 1000
* 1 pixel                 = 100 font units  (=> 10 px per em)
* baseline                = y 0
* cap height              = 7 px  (700)
* x-height                = 5 px  (500)
* descender               = -2 px (-200)
* math axis height        = 3 px  (300)  -- vertical centre of operators / bars

Every coordinate is an integer multiple of one pixel, which is what keeps the
output crisp: glyph edges always land on whole-pixel boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

# --- grid constants ---------------------------------------------------------
UPM = 1000
PIXEL = 100               # font units per pixel
CAP_PX = 7
XHEIGHT_PX = 5
DESCENT_PX = -2
ASCENT_PX = 8
AXIS_PX = 3               # math axis height in pixels

CAP_HEIGHT = CAP_PX * PIXEL
X_HEIGHT = XHEIGHT_PX * PIXEL
DESCENT = DESCENT_PX * PIXEL          # negative
ASCENT = ASCENT_PX * PIXEL
# Math axis = 3.5 px. Monocraft centres binary operators (+ - =) on y=3.5px, so
# the fraction bar / delimiter centre must match or the engine shifts delimiters
# by half a pixel (which destroys pixel crispness).
AXIS_HEIGHT = 350


@dataclass
class Glyph:
    """A single pixel glyph.

    `rows` is a list of equal-length strings using '#'/'X' for an "on" pixel and
    anything else (typically '.') for "off". Row 0 is the TOP row. The bottom of
    the art sits on `baseline_row` measured from the BOTTOM of the art, so a
    glyph can descend below the baseline by giving it off-baseline rows.
    """

    name: str
    codepoint: int | None
    rows: list[str]
    advance_px: int
    # y (in pixels) of the bottom-most art row relative to the baseline.
    # 0 => art sits on the baseline; -2 => art bottom is two px below baseline.
    bottom_px: int = 0

    @property
    def width_px(self) -> int:
        return max((len(r) for r in self.rows), default=0)

    @property
    def height_px(self) -> int:
        return len(self.rows)


def _merge_horizontal_runs(rows: list[str]) -> list[tuple[int, int, int]]:
    """Collapse each row of on-pixels into horizontal runs.

    Returns (row_index_from_top, x_start_px, run_length) tuples. Merging runs
    keeps the contour count low versus emitting one square per pixel.
    """
    runs: list[tuple[int, int, int]] = []
    for r, row in enumerate(rows):
        x = 0
        n = len(row)
        while x < n:
            if row[x] in "#X":
                start = x
                while x < n and row[x] in "#X":
                    x += 1
                runs.append((r, start, x - start))
            else:
                x += 1
    return runs


def draw_glyph(glyph: Glyph) -> "TTGlyphPen":
    """Render a Glyph to a TTGlyphPen as axis-aligned rectangles.

    Each horizontal run of on-pixels becomes one rectangle contour wound
    clockwise. Overlapping/abutting rectangles fill correctly under the
    non-zero winding rule, so we do not need overlap removal for rendering.
    """
    pen = TTGlyphPen(None)
    rows = glyph.rows
    h = len(rows)
    # Pixel grid -> font units. The bottom art row maps to y = bottom_px*PIXEL.
    bottom = glyph.bottom_px * PIXEL
    for (r, x_start, length) in _merge_horizontal_runs(rows):
        # row 0 is the top; convert to y from baseline.
        y_top_px = (h - r)            # top edge of this pixel row, in px from art bottom
        y0 = bottom + (y_top_px - 1) * PIXEL    # bottom edge of the pixel row
        y1 = bottom + y_top_px * PIXEL          # top edge
        x0 = x_start * PIXEL
        x1 = (x_start + length) * PIXEL
        pen.moveTo((x0, y0))
        pen.lineTo((x0, y1))
        pen.lineTo((x1, y1))
        pen.lineTo((x1, y0))
        pen.closePath()
    return pen


@dataclass
class FontSpec:
    family: str = "MinecrafTeX Math"
    style: str = "Regular"
    version: str = "0.1.0"
    glyphs: list[Glyph] = field(default_factory=list)
    # Extra cmap entries: codepoint -> existing glyph name (aliases, no new
    # outline). Used to point the Mathematical Alphanumeric Symbols at the
    # plain pixel letters so math italic/bold/... letters render as pixels.
    extra_cmap: dict[int, str] = field(default_factory=dict)


def build_font(spec: FontSpec) -> TTFont:
    """Assemble a complete TTFont (without the MATH table) from glyph specs."""
    # .notdef first, then the rest.
    order = [".notdef"] + [g.name for g in spec.glyphs]

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)

    # cmap: codepoint -> glyph name (+ alias entries reusing existing glyphs)
    cmap = {g.codepoint: g.name for g in spec.glyphs if g.codepoint is not None}
    names = set(order)
    for cp, name in spec.extra_cmap.items():
        if cp not in cmap and name in names:
            cmap[cp] = name
    fb.setupCharacterMap(cmap)

    # outlines
    glyf: dict[str, object] = {}
    metrics: dict[str, tuple[int, int]] = {}

    notdef = TTGlyphPen(None)
    glyf[".notdef"] = notdef.glyph()
    metrics[".notdef"] = (6 * PIXEL, 0)

    for g in spec.glyphs:
        pen = draw_glyph(g)
        glyf[g.name] = pen.glyph()
        metrics[g.name] = (g.advance_px * PIXEL, 0)

    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT)

    name_strings = {
        "familyName": spec.family,
        "styleName": spec.style,
        "fullName": f"{spec.family} {spec.style}",
        "psName": (spec.family + "-" + spec.style).replace(" ", ""),
        "version": f"Version {spec.version}",
        "uniqueFontIdentifier": f"MinecrafTeX;{spec.family};{spec.version}",
    }
    fb.setupNameTable(name_strings)
    fb.setupOS2(sTypoAscender=ASCENT, sTypoDescender=DESCENT,
                usWinAscent=ASCENT, usWinDescent=-DESCENT,
                sxHeight=X_HEIGHT, sCapHeight=CAP_HEIGHT)
    fb.setupPost()

    return fb.font


def save(font: TTFont, path: str) -> None:
    font.save(path)
