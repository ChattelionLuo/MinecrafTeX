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


def _rows_from_pixels(pixels: list[list[int]]) -> list[str]:
    return ["".join("#" if cell else "." for cell in row) for row in pixels]


def load_base_glyphs(max_codepoint: int = 0x10FFFF) -> list[Glyph]:
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
        glyphs.append(Glyph(
            name=e["name"],
            codepoint=cp,
            rows=rows,
            advance_px=_DEFAULT_ADVANCE_PX,
            bottom_px=-int(e.get("descent", 0)),
        ))
    return glyphs
