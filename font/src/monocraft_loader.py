"""Load Minecraft-style base glyphs from Monocraft's characters.json.

Monocraft (SIL OFL 1.1) stores each glyph as a row-major matrix of 0/1 pixels
plus an optional `descent` (how many pixels the art drops below the baseline).
That maps directly onto the MinecrafTeX grid: one matrix cell == one pixel, and
`bottom_px = -descent`.

We import this base set so prose text and math letters/operators all exist as
authentic pixels; MinecrafTeX then layers its own OpenType MATH machinery
(stretchy delimiters, display operators, radical) on top -- see math_glyphs.py.
"""
from __future__ import annotations

import json
import os

from pixelfont import Glyph

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "monocraft_characters.json")

# Advance width Monocraft uses for almost every glyph (PIXEL_SIZE * 6).
_DEFAULT_ADVANCE_PX = 6

# A few math-heavy marks look loose if they keep the monospace text advance.
# Keep the pixel art itself, but give narrow marks and fences tighter metrics so
# formulas such as f'(x) and |x| read like math, not fixed-width prose.
_ADVANCE_OVERRIDES_PX = {
    0x0027: 3,  # apostrophe
    0x007C: 4,  # vertical bar
    0x2016: 5,  # double vertical line
    0x2032: 3,  # prime
    0x2033: 4,  # double prime
    0x2034: 5,  # triple prime
}

_CENTERED_TIGHT_MARKS = set(_ADVANCE_OVERRIDES_PX)


def _ink_bounds_px(rows: list[str]) -> tuple[int, int] | None:
    xs = [x for row in rows for x, cell in enumerate(row) if cell == "#"]
    if not xs:
        return None
    return min(xs), max(xs) + 1


def _center_offset_px(rows: list[str], advance_px: float) -> float:
    bounds = _ink_bounds_px(rows)
    if bounds is None:
        return 0.0
    left, right = bounds
    return (advance_px - (right - left)) / 2 - left


def _proportional_advance_px(cp: int, rows: list[str]) -> float:
    override = _ADVANCE_OVERRIDES_PX.get(cp)
    if override is not None:
        return override
    bounds = _ink_bounds_px(rows)
    if bounds is None:
        return 4
    left, right = bounds
    # Keep one pixel of total side bearing around the visible ink while allowing
    # naturally wider Monocraft glyphs (arrows, symbols) to remain wide.
    return max(2, right - left + 1)


def _rows_from_pixels(pixels: list[list[int]]) -> list[str]:
    return ["".join("#" if cell else "." for cell in row) for row in pixels]


def load_base_glyphs(max_codepoint: int = 0x10FFFF,
                     proportional: bool = False) -> list[Glyph]:
    """Return every Monocraft glyph with a real codepoint up to `max_codepoint`.

    By default we load the whole set (Latin, Greek, Cyrillic, punctuation,
    arrows, mathematical operators, ...) so prose and math symbols all exist as
    authentic pixels.
    """
    with open(_DATA, encoding="utf-8") as fh:
        entries = json.load(fh)

    glyphs: list[Glyph] = []
    seen: set[int] = set()
    for e in entries:
        cp = e.get("codepoint")
        if cp is None or cp < 0x20 or cp > max_codepoint:
            continue
        if cp in seen:
            continue
        if "pixels" not in e or not e["pixels"]:
            continue
        seen.add(cp)
        rows = _rows_from_pixels(e["pixels"])
        advance_px = (_proportional_advance_px(cp, rows) if proportional
                      else _ADVANCE_OVERRIDES_PX.get(cp, _DEFAULT_ADVANCE_PX))
        if proportional:
            x_offset_px = _center_offset_px(rows, advance_px)
        elif cp in _CENTERED_TIGHT_MARKS:
            x_offset_px = _center_offset_px(rows, advance_px)
        else:
            x_offset_px = float(e.get("leftMargin", 0))
        glyphs.append(Glyph(
            name=e["name"],
            codepoint=cp,
            rows=rows,
            advance_px=advance_px,
            x_offset_px=x_offset_px,
            bottom_px=-int(e.get("descent", 0)),
        ))
    return glyphs
