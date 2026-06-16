"""Build MinecrafTeX-Math.ttf (and .woff2) from pixel glyph definitions.

Pipeline:
  1. Base pixel glyphs imported from Monocraft (Latin, Greek, operators, ...).
  2. MinecrafTeX's own math glyphs layered on top (radical, stretchy delimiter
     size variants + assembly parts, display-size big operators).
  3. OpenType MATH table (constants + MathVariants for adaptive sizing).
  4. GSUB `math` script so unicode-math adopts the font as primary.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pixelfont import FontSpec, build_font, save  # noqa: E402
from monocraft_loader import load_base_glyphs  # noqa: E402
from math_glyphs import math_extra_glyphs  # noqa: E402
from math_alphanum import alphanumeric_aliases  # noqa: E402
from math_table import add_math_table  # noqa: E402
from gsub import add_math_script  # noqa: E402

DIST = os.path.join(os.path.dirname(__file__), "dist")

# Delimiters whose base pixel art Monocraft draws from the baseline up to cap
# height (0..7 px). Lowering them one pixel (to -1..6 px) centres them on the
# x-height content they usually wrap, so plain `(x)`, `[x]`, `{x}`, `|x|` look
# balanced instead of the glyph sitting high above the letter. Big delimiters use
# \left\right, which the engine re-centres on the math axis, so they are
# unaffected.
_DELIMITER_DROP_CODEPOINTS = {
    0x0028, 0x0029,  # ( )
    0x005B, 0x005D,  # [ ]
    0x007B, 0x007D,  # { }
    0x007C,          # |
    0x2016,          # ‖
    0x2308, 0x2309,  # ⌈ ⌉
    0x230A, 0x230B,  # ⌊ ⌋
    0x27E8, 0x27E9,  # ⟨ ⟩
}

# Long arrows (and similar) that unicode-math may request; reuse the base
# short-arrow pixel glyph rather than duplicating outlines.
_SYMBOL_ALIASES = {
    0x27F9: 0x21D2,  # long rightwards double arrow -> rightwards double arrow
    0x27F8: 0x21D0,  # long leftwards double arrow  -> leftwards double arrow
    0x27FA: 0x21D4,  # long left-right double arrow -> left-right double arrow
    0x27F6: 0x2192,  # long rightwards arrow        -> rightwards arrow
    0x27F5: 0x2190,  # long leftwards arrow         -> leftwards arrow
    0x27F7: 0x2194,  # long left-right arrow        -> left-right arrow
}


def collect_glyphs():
    base = load_base_glyphs()
    # Drop the common delimiters 1 px so they centre on x-height content.
    for g in base:
        if g.codepoint in _DELIMITER_DROP_CODEPOINTS:
            g.bottom_px -= 1
    taken = {g.codepoint for g in base}
    glyphs = list(base)
    # Add MinecrafTeX math glyphs; for cmap'd ones, don't collide with base.
    for g in math_extra_glyphs():
        if g.codepoint is not None and g.codepoint in taken:
            continue
        glyphs.append(g)
    return glyphs


def main() -> None:
    os.makedirs(DIST, exist_ok=True)
    glyphs = collect_glyphs()
    # Alias the Mathematical Alphanumeric Symbols (math italic/bold/... letters
    # and digits) onto the plain pixel glyphs so they render as pixels.
    name_by_cp = {g.codepoint: g.name for g in glyphs if g.codepoint is not None}
    aliases = alphanumeric_aliases(name_by_cp)
    # A few long/extra symbols unicode-math requests that reuse a base glyph.
    for cp, base_cp in _SYMBOL_ALIASES.items():
        base = name_by_cp.get(base_cp)
        if base is not None and cp not in name_by_cp:
            aliases.setdefault(cp, base)
    spec = FontSpec(glyphs=glyphs, extra_cmap=aliases)
    font = build_font(spec)
    add_math_table(font)
    add_math_script(font, anchor_glyph="space")
    print(f"glyphs: {len(glyphs)}  alphanumeric aliases: {len(aliases)}")

    ttf_path = os.path.join(DIST, "MinecrafTeX-Math.ttf")
    save(font, ttf_path)
    print(f"wrote {ttf_path}")

    try:
        font.flavor = "woff2"
        woff2_path = os.path.join(DIST, "MinecrafTeX-Math.woff2")
        font.save(woff2_path)
        print(f"wrote {woff2_path}")
    except Exception as exc:  # pragma: no cover - optional dependency
        print(f"skipped woff2 ({exc}); run 'pip install brotli' to enable")


if __name__ == "__main__":
    main()
