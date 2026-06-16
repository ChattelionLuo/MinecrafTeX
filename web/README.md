# MinecrafTeX (web)

Render real LaTeX math as Minecraft pixels in the browser, using
[Temml](https://temml.org) (LaTeX → MathML) plus the MinecrafTeX pixel
OpenType **MATH** font. The browser's native MathML engine does the layout and
reads the font's MATH table.

## Quick start

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/temml/dist/Temml-Local.css" />
<script src="https://cdn.jsdelivr.net/npm/temml/dist/temml.min.js"></script>
<script type="module">
  import { injectFont, renderMath } from "./src/index.js";
  injectFont("../font/dist/MinecrafTeX-Math.woff2");
  renderMath(String.raw`\frac{\sqrt{x}}{n} = \sum_{k} a_k`,
             document.getElementById("eq"));
</script>
<div id="eq"></div>
```

See [`demo/index.html`](demo/index.html) for a full page. Native MathML support
is best in Firefox.

## Verify

```bash
npm install temml
node verify.js     # checks LaTeX -> MathML conversion for sample equations
```
