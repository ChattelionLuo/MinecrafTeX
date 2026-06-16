# MinecrafTeX roadmap

### Phase 0 — Scaffolding & licensing ✅
- Repo layout, OFL (font) + MIT (tooling), Monocraft attribution.

### Phase 1 — Font build pipeline ✅ (core proven)
- Pure-Python pixel→OpenType builder (`font/src/pixelfont.py`).
- Pixel-snapped grid (UPM 1000, 1px = 100 units).
- Builds `.ttf` + `.woff2`; validated and round-tripped.

### Phase 2 — Math glyph coverage 🚧
- Full set: Latin + Greek, digits, binary/relational operators, set/logic,
  calculus, big operators, delimiters, dots.
- Currently: just the proof-of-concept subset.

### Phase 3 — OpenType MATH table 🚧
- ✅ `MathConstants` (all values pixel-snapped).
- ⬜ `MathVariants` + glyph **assembly** for stretchy `( ) { } | √ ∫` and
  over/under-braces (top/extender/bottom pixel pieces).
- ⬜ `MathGlyphInfo`: italic corrections, math kerning, accents.
- ⬜ Discrete hand-designed script / scriptscript sizes (crispness).

### Phase 4 — LaTeX package 🚧
- ✅ `latex/minecraftex.sty` wrapper over `fontspec` + `unicode-math`;
  compiles with lualatex, pixel font used for text.
- ⬜ Make unicode-math accept it as the *primary* math font: needs the Unicode
  math-alphanumeric glyphs, `MathVariants`, and the `ssty` script-size feature
  (otherwise it overlays Latin Modern for missing symbols).
- ⬜ Package options polish, CTAN packaging.

### Phase 5 — Web library 🚧
- ✅ `web/` Temml LaTeX→MathML verified (`node verify.js`); `@font-face` + JS API.
- ⬜ MathJax fallback; React component; live playground.

### Phase 6 — Distribution
- Font: GitHub Releases / Fontsource. LaTeX: CTAN → TeX Live/MikTeX.
  Web: npm + jsDelivr.

### Phase 7 — Testing / CI
- Golden-image visual regression (PDF + web); fontbakery + MATH sanity in CI.

## Known design polish items
- Summation (Σ) diagonal and radical (√) extension need refinement.
- Decide upright vs slanted math italics.
