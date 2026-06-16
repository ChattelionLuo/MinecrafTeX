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
- Hand-built additions Monocraft lacks: radical `√` and n-ary product `∏`.
- Display-size big operators (`∫ ∑ ∏`) and stretchy delimiter pieces.

### Phase 3 — OpenType MATH table ✅ (core feature)
- ✅ `MathConstants` (all values pixel-snapped).
- ✅ `MathVariants` + glyph **assembly** for stretchy `( ) [ ] { } | √ ∫ ∑ ∏`
  (size variants + top/extender/bottom pixel pieces; 1 px growth steps stay crisp).
- ✅ `MathGlyphInfo`: italic corrections so integral limits clear the glyph.
- ⬜ Discrete hand-designed script / scriptscript sizes (further crispness).

### Phase 4 — LaTeX package ✅ (working)
- ✅ `latex/minecraftex.sty` wrapper over `fontspec` + `unicode-math`;
  compiles with lualatex, pixel font used for text and math.
- ✅ Accepted as the *primary* math font: a `math` script tag in GSUB stops the
  Latin Modern fallback; `example.tex` renders fully in pixels with no missing chars.
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
