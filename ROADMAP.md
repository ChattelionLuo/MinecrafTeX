# MinecrafTeX roadmap

### Phase 0 — Scaffolding & licensing ✅
- Repo layout, OFL (font) + MIT (tooling), Monocraft attribution.

### Phase 1 — Font build pipeline ✅ (core proven)
- Pure-Python pixel→OpenType builder (`font/src/pixelfont.py`).
- Pixel-snapped grid (UPM 1000, 1px = 100 units).
- Builds `.ttf` + `.woff2`; validated and round-tripped.

### Phase 2 — Math glyph coverage ✅ (broad)
- Full Unicode coverage loaded from Monocraft: Latin + Greek, digits,
  binary/relational operators, set/logic, calculus, big operators, delimiters, dots.
- Mathematical Alphanumeric Symbols (U+1D400–U+1D7FF): all 1000+ bold/italic/
  script/fraktur/double-struck/sans/mono letter & digit planes aliased onto the
  base pixel glyphs, so math letters render as pixels (no Latin Modern fallback).
  Greek "symbol variants" (italic phi etc.) fall back to the plain Greek letter.
- Hand-built additions Monocraft lacks: radical `√`, n-ary product `∏`, and the
  common relations/operators `≤ ≥ ≈ ∼ ∈ ∋ ∇ ⋅ ∪ ∅`; long arrows alias short ones.
- Display-size big operators (`∫ ∑ ∏`) and stretchy delimiter pieces.

### Phase 3 — OpenType MATH table ✅ (core feature)
- ✅ `MathConstants` (pixel-snapped; math axis on the half-pixel grid at 3.5 px to
  match Monocraft's `+ − =` operator centring, so stretchy delimiters stay crisp).
- ✅ `MathVariants` + glyph **assembly** for stretchy `( ) [ ] { } | √ ∫ ∑ ∏`
  (size variants up to 25 px + top/extender/bottom pixel pieces; 1 px growth steps
  stay crisp). Curved delimiters drawn 2 px edge-connected to read as solid pixels.
- ✅ `MathGlyphInfo`: italic corrections so integral limits clear the glyph.
- ⬜ Discrete hand-designed script / scriptscript sizes (further crispness).

### Phase 4 — LaTeX package ✅ (working)
- ✅ `latex/minecraftex.sty` wrapper over `fontspec` + `unicode-math`;
  compiles with lualatex, pixel font used for text and math.
- ✅ Accepted as the *primary* math font: a `math` script tag in GSUB stops the
  Latin Modern fallback; `latex/example.tex` is a two-page math article (fractions,
  roots, calculus, series/products, matrices, cases, Greek, relations) that renders
  fully in pixels with adaptive sizing and **no missing characters**.
- ⬜ Package options polish, CTAN packaging.

### Phase 5 — Web library 🚧
- ✅ `web/` Temml LaTeX→MathML verified (`node verify.js`); confirms stretchy
  fences + `mfrac`/`msqrt`/`munderover` structure; `@font-face` + JS API + demo.
- ⬜ MathJax fallback; React component; live playground.

### Phase 6 — Distribution
- Font: GitHub Releases / Fontsource. LaTeX: CTAN → TeX Live/MikTeX.
  Web: npm + jsDelivr.

### Phase 7 — Testing / CI
- Golden-image visual regression (PDF + web); fontbakery + MATH sanity in CI.

## Known design polish items
- Decide upright vs slanted math italics.
- Hand-design script / scriptscript pixel sizes for deeply nested scripts.
