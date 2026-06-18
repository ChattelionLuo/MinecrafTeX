const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..");
const sourceDir = path.join(root, "font", "dist");
const targetDir = path.join(__dirname, "..", "dist");
const files = ["MinecrafTeX-Math.ttf", "MinecrafTeX-Math.woff2"];

fs.mkdirSync(targetDir, { recursive: true });

for (const file of files) {
  const source = path.join(sourceDir, file);
  const target = path.join(targetDir, file);
  if (!fs.existsSync(source)) {
    throw new Error(`Missing ${source}. Run python font/build_font.py first.`);
  }
  fs.copyFileSync(source, target);
  console.log(`copied ${path.relative(root, target)}`);
}