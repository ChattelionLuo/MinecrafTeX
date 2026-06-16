// Verify the web path: LaTeX -> MathML via Temml for the demo equation.
const temml = require("temml");

const equations = [
  String.raw`\int_{0}^{1} \frac{\sqrt{x}}{n}\,dx = \sum_{k} a_k`,
  String.raw`a + n = k`,
];

for (const tex of equations) {
  const mml = temml.renderToString(tex, { displayMode: true });
  const ok = mml.startsWith("<math") && mml.includes("</math>");
  console.log(ok ? "OK  " : "FAIL", tex);
  if (!ok) {
    console.log(mml);
    process.exit(1);
  }
}
// Show the structural tags Temml emits (these are what the font styles).
const sample = temml.renderToString(equations[0], { displayMode: true });
const tags = [...sample.matchAll(/<(m[a-z]+)/g)].map((m) => m[1]);
console.log("MathML elements used:", [...new Set(tags)].join(", "));
console.log("PASS: LaTeX -> MathML conversion works");
