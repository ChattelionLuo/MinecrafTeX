# MinecrafTeX

> Real LaTeX math — rendered entirely in authentic Minecraft pixel art.

MinecrafTeX lets you typeset ordinary math (`\frac`, `\sqrt`, `\int`, `\sum`,
sub/superscripts, big delimiters …) using normal LaTeX/AMS syntax, but every
glyph and every structural rule (fraction bars, radical vinculums, stretchy
braces) is drawn as crisp Minecraft-style pixels.

It works in **two places from one shared font**:

* **LaTeX → PDF** via LuaLaTeX/XeLaTeX (`minecraftex.sty`)
* **The web** via [Temml](https://temml.org) (LaTeX → MathML) + the font

## Why this works (the core idea)

We do **not** rewrite a math engine. We build **one OpenType font with a MATH
table** in a pixel style, then let proven engines do the layout:

| Layer | Tech | Role |
|-------|------|------|
| Font  | fontTools (pure Python) | pixel glyphs + OpenType **MATH** table |
| LaTeX | `fontspec` + `unicode-math` | loads the font as the math font |
| Web   | `Temml` + native MathML | browser renders MathML with the font |

The MATH table is what teaches each engine how to size a fraction bar, stretch
an integral, grow braces, and place scripts — so faithful math layout comes
"for free," just with Minecraft pixels.

## Repository layout

```
font/      pixel-font build pipeline (Python + fontTools, no FontForge needed)
  src/       pixelfont.py, monocraft_loader.py, math_glyphs.py,
             math_alphanum.py, math_table.py, gsub.py
  build_font.py
  dist/      built MinecrafTeX-Math.ttf / .woff2
latex/     minecraftex.sty + example documents (example.tex, clt.tex)
web/       npm package + browser demo (Temml)
tests/     validation + rendered samples
```

## Build the font

```bash
pip install fonttools brotli
python font/build_font.py        # -> font/dist/MinecrafTeX-Math.ttf + .woff2
python tests/validate.py         # sanity-check + render sample PNGs
```

The whole grid is pixel-snapped: `UPM = 1000`, `1px = 100 units`, so every
edge, bar and gap lands on a whole-pixel boundary and stays sharp.

## Status

The font core (pixel→OpenType + MATH table) builds, validates, round-trips and
renders. Coverage is broad: the full Monocraft glyph set plus the Mathematical
Alphanumeric Symbols block (so math letters render as pixels), the common
relations and operators Monocraft lacks, a growing radical, display-size big
operators, and stretchy delimiters with proper OpenType `MathVariants`/assembly.
Two worked LaTeX documents render fully in pixels with adaptive sizing:
[`latex/example.tex`](latex/example.tex) (a two-page math showcase) and
[`latex/clt.tex`](latex/clt.tex) (a short proof of the Central Limit Theorem).
See [`ROADMAP.md`](ROADMAP.md).

## Licensing

* **Font** (`font/`, `dist/*.ttf`, `*.woff2`): SIL Open Font License 1.1
  (`OFL.txt`). Derived from [Monocraft](https://github.com/IdreesInc/Monocraft)
  by Idrees Hassan, also OFL 1.1 — see [`NOTICE`](NOTICE).
* **Tooling and wrappers** (`font/src` build scripts, `latex/`, `web/`):
  MIT (`LICENSE`).

"Minecraft" is a trademark of Mojang/Microsoft; this project is unaffiliated and
uses no Minecraft game assets.
