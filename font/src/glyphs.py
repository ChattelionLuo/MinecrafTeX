"""Pixel-art glyph definitions for the MinecrafTeX proof-of-concept.

Each entry is row-major, top row first, '#' = on pixel, '.' = off. Just enough
coverage to render an equation exercising fractions, scripts, a radical and a
big operator:  Sum, integral, sqrt, fraction bar, '=', digits and letters.
"""
from __future__ import annotations

from pixelfont import Glyph

# Helper to trim trailing empty designing comments; rows are plain strings.

GLYPHS: list[Glyph] = [
    # --- space ---
    Glyph("space", 0x0020, [], advance_px=6),

    # --- digits ---
    Glyph("zero", 0x0030, [
        ".###.",
        "#...#",
        "#..##",
        "#.#.#",
        "##..#",
        "#...#",
        ".###.",
    ], advance_px=6),
    Glyph("one", 0x0031, [
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ], advance_px=6),

    # --- lowercase letters (x-height 5, ascenders reach 7) ---
    Glyph("x", 0x0078, [
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
    ], advance_px=6),
    Glyph("n", 0x006E, [
        "#.##.",
        "##..#",
        "#...#",
        "#...#",
        "#...#",
    ], advance_px=6),
    Glyph("d", 0x0064, [
        "....#",
        "....#",
        ".####",
        "#...#",
        "#...#",
        "#...#",
        ".####",
    ], advance_px=6),
    Glyph("a", 0x0061, [
        ".###.",
        "....#",
        ".####",
        "#...#",
        ".####",
    ], advance_px=6),
    Glyph("k", 0x006B, [
        "#....",
        "#....",
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
    ], advance_px=6),

    # --- operators ---
    Glyph("equal", 0x003D, [
        "#####",
        ".....",
        ".....",
        "#####",
    ], advance_px=6, bottom_px=2),
    Glyph("slash", 0x002F, [
        "....#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#....",
    ], advance_px=6),
    Glyph("minus", 0x2212, [
        "#####",
    ], advance_px=6, bottom_px=3),
    Glyph("plus", 0x002B, [
        "..#..",
        "..#..",
        "#####",
        "..#..",
        "..#..",
    ], advance_px=6, bottom_px=1),

    # --- math operators ---
    # Radical: rising tick on the left, short vinculum top-right.
    Glyph("radical", 0x221A, [
        "....###",
        "....#..",
        "....#..",
        "....#..",
        "#...#..",
        ".#..#..",
        ".#.#...",
        "..#....",
    ], advance_px=8),
    # Integral: tall slim S with hooks.
    Glyph("integral", 0x222B, [
        "..##",
        ".#.#",
        ".#..",
        ".#..",
        ".#..",
        ".#..",
        ".#..",
        ".#..",
        "#.#.",
        "##..",
    ], advance_px=5, bottom_px=-2),
    # Summation: big sigma.
    Glyph("summation", 0x2211, [
        "######",
        "#....#",
        ".#...#",
        "..#...",
        ".#...#",
        "#....#",
        "######",
    ], advance_px=7),
]
