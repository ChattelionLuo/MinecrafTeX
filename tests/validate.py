"""Validate the built font: MATH table round-trip + render samples to PNG."""
import os
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTF = os.path.join(ROOT, "font", "dist", "MinecrafTeX-Math.ttf")

f = TTFont(TTF)
print("tables:", sorted(f.keys()))
m = f["MATH"].table.MathConstants
print("AxisHeight:", m.AxisHeight.Value)
print("FractionRuleThickness:", m.FractionRuleThickness.Value)
print("ScriptPercentScaleDown:", m.ScriptPercentScaleDown)
cmap = f.getBestCmap()
print("cmap count:", len(cmap))
for cp, label in [(0x222B, "integral"), (0x2211, "sum"), (0x221A, "sqrt"),
                  (0x2212, "minus"), (0x003D, "equal")]:
    print(f"has {label} (U+{cp:04X}):", cp in cmap)

# Round-trip: save and reload to confirm the MATH table compiles cleanly.
tmp = os.path.join(ROOT, "tests", "_roundtrip.ttf")
f.save(tmp)
g = TTFont(tmp)
assert g["MATH"].table.MathConstants.FractionRuleThickness.Value == 100
os.remove(tmp)
print("MATH round-trip: OK")

# Render samples with Pillow.
from PIL import Image, ImageFont, ImageDraw
fnt = ImageFont.truetype(TTF, 80)
img = Image.new("RGB", (760, 140), "white")
d = ImageDraw.Draw(img)
d.text((10, 20), "0 1 x n d a k = / + \u2212 \u222B \u2211 \u221A",
       font=fnt, fill="black")
out = os.path.join(ROOT, "tests", "sample_glyphs.png")
img.save(out)
print("rendered:", out)
