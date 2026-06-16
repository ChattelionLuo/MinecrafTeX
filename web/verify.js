// Verify the web path: LaTeX -> MathML via Temml for the demo equations.
// The adaptive sizing itself is performed by the browser's native MathML engine
// reading our OpenType MATH table; here we confirm Temml emits the stretchy
// structure (mo stretchy="true", mfrac, msqrt, munderover) that drives it.
const temml = require("temml");

const equations = [
  String.raw`\left( \frac{\sqrt{x}}{n} \right) = \int_{0}^{1} \sqrt{x}\,dx = \sum_{k=1}^{n} a_k`,
  String.raw`f(x) = \left( 1 + \cfrac{1}{1 + \frac{1}{x}} \right)`,
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

// Confirm the adaptive structures Temml emits (these are what the MATH table grows).
const sample = temml.renderToString(equations[0], { displayMode: true });
const tags = [...sample.matchAll(/<(m[a-z]+)/g)].map((m) => m[1]);
const fences = (sample.match(/fence="true"/g) || []).length;
console.log("MathML elements used:", [...new Set(tags)].join(", "));
console.log("Stretchy fence operators emitted:", fences);
for (const need of ["mfrac", "msqrt", "munderover"]) {
  if (!tags.includes(need)) {
    console.log("FAIL: expected", need, "in MathML");
    process.exit(1);
  }
}
if (fences < 1) {
  console.log("FAIL: expected at least one stretchy fence operator");
  process.exit(1);
}
console.log("PASS: LaTeX -> MathML conversion works with adaptive structure");
