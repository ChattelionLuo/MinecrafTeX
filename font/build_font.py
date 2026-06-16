"""Build MinecrafTeX-Math.ttf (and .woff2) from pixel glyph definitions."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pixelfont import FontSpec, build_font, save  # noqa: E402
from glyphs import GLYPHS  # noqa: E402
from math_table import add_math_table  # noqa: E402

DIST = os.path.join(os.path.dirname(__file__), "dist")


def main() -> None:
    os.makedirs(DIST, exist_ok=True)
    spec = FontSpec(glyphs=GLYPHS)
    font = build_font(spec)
    add_math_table(font)

    ttf_path = os.path.join(DIST, "MinecrafTeX-Math.ttf")
    save(font, ttf_path)
    print(f"wrote {ttf_path}")

    # Web build: woff2 (requires the 'brotli' package; skip gracefully if absent)
    try:
        font.flavor = "woff2"
        woff2_path = os.path.join(DIST, "MinecrafTeX-Math.woff2")
        font.save(woff2_path)
        print(f"wrote {woff2_path}")
    except Exception as exc:  # pragma: no cover - optional dependency
        print(f"skipped woff2 ({exc}); run 'pip install brotli' to enable")


if __name__ == "__main__":
    main()
