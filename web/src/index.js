// MinecrafTeX web API (thin wrapper around Temml).
//
//   import { renderMath, injectFont } from "minecraftex";
//   injectFont("/fonts/MinecrafTeX-Math.woff2");
//   renderMath("\\frac{\\sqrt{x}}{n}", document.getElementById("eq"));
//
// Temml is a peer dependency; the caller provides it (CDN or bundler).

export function injectFont(woff2Url, fontFamily = "MinecrafTeX Math") {
  const style = document.createElement("style");
  style.textContent = `
    @font-face {
      font-family: "${fontFamily}";
      src: url("${woff2Url}") format("woff2");
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
