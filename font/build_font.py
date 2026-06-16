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
from math_table import add_math_table  # noqa: E402
from gsub import add_math_script  # noqa: E402

DIST = os.path.join(os.path.dirname(__file__), "dist")


def collect_glyphs():
    base = load_base_glyphs()
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
    spec = FontSpec(glyphs=glyphs)
    font = build_font(spec)
    add_math_table(font)
    add_math_script(font, anchor_glyph="space")
    print(f"glyphs: {len(glyphs)}")

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
