// MinecrafTeX web API (thin wrapper around Temml).
//
//   import { renderMath, injectFont } from "minecraftex";
//   injectFont("/fonts/MinecrafTeX-Math-Proportional.woff2");
//   renderMath("\\frac{\\sqrt{x}}{n}", document.getElementById("eq"));
//
// Temml is a peer dependency; the caller provides it (CDN or bundler).

export function injectFont(woff2Url, fontFamily = "MinecrafTeX Math", variants = {}) {
  const boldUrl = variants.boldUrl || woff2Url.replace(/\.woff2$/i, "-Bold.woff2");
  const italicUrl = variants.italicUrl || woff2Url.replace(/\.woff2$/i, "-Italic.woff2");
  const boldItalicUrl = variants.boldItalicUrl || woff2Url.replace(/\.woff2$/i, "-BoldItalic.woff2");
  const style = document.createElement("style");
  style.textContent = `
    @font-face {
      font-family: "${fontFamily}";
      src: url("${woff2Url}") format("woff2");
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }
    @font-face {
      font-family: "${fontFamily}";
      src: url("${boldUrl}") format("woff2");
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }
    @font-face {
      font-family: "${fontFamily}";
      src: url("${italicUrl}") format("woff2");
      font-weight: 400;
      font-style: italic;
      font-display: swap;
    }
    @font-face {
      font-family: "${fontFamily}";
      src: url("${boldItalicUrl}") format("woff2");
      font-weight: 700;
      font-style: italic;
      font-display: swap;
    }
    math, math * { font-family: "${fontFamily}", serif !important; }
  `;
  document.head.appendChild(style);
}

export function renderMath(latex, element, { displayMode = true } = {}) {
  if (typeof temml === "undefined") {
    throw new Error("Temml not found. Load temml before calling renderMath.");
  }
  // eslint-disable-next-line no-undef
  temml.render(latex, element, { displayMode });
}
