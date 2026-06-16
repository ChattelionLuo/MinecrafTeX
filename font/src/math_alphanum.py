"""Map the Mathematical Alphanumeric Symbols block to the plain pixel letters.

unicode-math (and MathML renderers) remap ordinary math letters/digits to the
Mathematical Alphanumeric Symbols block (U+1D400-U+1D7FF): e.g. a math italic
``x`` is requested as U+1D465, a bold ``A`` as U+1D400, and so on.  Monocraft has
none of these, so without them every math *letter* falls back to Latin Modern
(the small serif italics seen in the broken renders).

MinecrafTeX has a single upright pixel style, so we simply alias every style
plane (bold, italic, script, fraktur, double-struck, sans, monospace, ...) back
to the same base pixel glyph.  That keeps all math letters as authentic pixels
and lets unicode-math accept the font as a complete primary math font.

`alphanumeric_aliases(name_by_cp)` returns ``{codepoint: glyph_name}`` aliases,
reusing existing glyph outlines (no duplicated contours).
"""
from __future__ import annotations

# (capital_A_start, small_a_start) for each Latin style plane.
_LATIN_PLANES = [
    (0x1D400, 0x1D41A),  # bold
    (0x1D434, 0x1D44E),  # italic
    (0x1D468, 0x1D482),  # bold italic
    (0x1D49C, 0x1D4B6),  # script
    (0x1D4D0, 0x1D4EA),  # bold script
    (0x1D504, 0x1D51E),  # fraktur
    (0x1D538, 0x1D552),  # double-struck
    (0x1D56C, 0x1D586),  # bold fraktur
    (0x1D5A0, 0x1D5BA),  # sans-serif
    (0x1D5D4, 0x1D5EE),  # sans-serif bold
    (0x1D608, 0x1D622),  # sans-serif italic
    (0x1D63C, 0x1D656),  # sans-serif bold italic
    (0x1D670, 0x1D68A),  # monospace
]

# Digit plane starts (each covers 0-9).
_DIGIT_PLANES = [0x1D7CE, 0x1D7D8, 0x1D7E2, 0x1D7EC, 0x1D7F6]

# Letterlike Symbols that fill the "holes" of the math alphanumeric planes;
# unicode-math requests these BMP codepoints instead of the reserved 1D4xx slot.
# codepoint -> base ASCII letter.
_LETTERLIKE = {
    0x210E: "h",  # italic h (Planck constant)
    0x212C: "B", 0x2130: "E", 0x2131: "F", 0x210B: "H", 0x2110: "I",
    0x2112: "L", 0x2133: "M", 0x211B: "R", 0x212F: "e", 0x210A: "g",
    0x2134: "o",  # script
    0x212D: "C", 0x210C: "H", 0x2111: "I", 0x211C: "R", 0x2128: "Z",  # fraktur
    0x2102: "C", 0x210D: "H", 0x2115: "N", 0x2119: "P", 0x211A: "Q",
    0x211D: "R", 0x2124: "Z",  # double-struck
}

# Ordered base codepoints for the math Greek CAPITAL planes (25 slots):
# Alpha..Rho, THETA SYMBOL, Sigma..Omega, NABLA.
_GREEK_CAP_ORDER = (
    list(range(0x391, 0x3A2))      # Alpha..Rho (0x391..0x3A1)
    + [0x3F4]                       # GREEK CAPITAL THETA SYMBOL
    + list(range(0x3A3, 0x3AA))     # Sigma..Omega
    + [0x2207]                      # NABLA
)
# Ordered base codepoints for the math Greek SMALL planes (25 + variants):
# alpha..omega, PARTIAL, epsilon/theta/kappa/phi/rho/pi symbols.
_GREEK_SMALL_ORDER = (
    list(range(0x3B1, 0x3CA))       # alpha..omega (includes final sigma 0x3C2)
    + [0x2202, 0x3F5, 0x3D1, 0x3F0, 0x3D5, 0x3F1, 0x3D6]
)
# Some Greek "symbol variant" codepoints (phi/theta/kappa/... symbols) and NABLA
# are referenced by the math-alphanumeric Greek planes but are not present as
# distinct pixel glyphs.  Fall back to the plain Greek letter so e.g. math italic
# phi (U+1D719 -> base U+03D5 phi symbol) still renders instead of vanishing.
_GREEK_SYMBOL_FALLBACK = {
    0x3F4: 0x398,  # GREEK CAPITAL THETA SYMBOL -> Theta
    0x3F5: 0x3B5,  # GREEK LUNATE EPSILON SYMBOL -> epsilon
    0x3D1: 0x3B8,  # GREEK THETA SYMBOL -> theta
    0x3D5: 0x3C6,  # GREEK PHI SYMBOL -> phi
    0x3F0: 0x3BA,  # GREEK KAPPA SYMBOL -> kappa
    0x3F1: 0x3C1,  # GREEK RHO SYMBOL -> rho
    0x3D6: 0x3C0,  # GREEK PI SYMBOL -> pi
}

# (capital_start, small_start) for the bold and italic Greek planes.
_GREEK_PLANES = [
    (0x1D6A8, 0x1D6C2),  # bold
    (0x1D6E2, 0x1D6FC),  # italic
    (0x1D71C, 0x1D736),  # bold italic
    (0x1D756, 0x1D770),  # sans-serif bold
    (0x1D790, 0x1D7AA),  # sans-serif bold italic
]


def alphanumeric_aliases(name_by_cp: dict[int, str]) -> dict[int, str]:
    """Return {codepoint: glyph_name} aliasing math alphanumerics to base glyphs.

    Only entries whose base glyph actually exists are emitted.
    """
    out: dict[int, str] = {}

    def alias(cp: int, base_cp: int) -> None:
        name = name_by_cp.get(base_cp)
        if name is None:
            fallback = _GREEK_SYMBOL_FALLBACK.get(base_cp)
            if fallback is not None:
                name = name_by_cp.get(fallback)
        if name is not None:
            out[cp] = name

    # Latin letters: A-Z then a-z for every style plane.
    for cap_start, small_start in _LATIN_PLANES:
        for i in range(26):
            alias(cap_start + i, ord("A") + i)
            alias(small_start + i, ord("a") + i)

    # Digits 0-9 for every digit plane.
    for start in _DIGIT_PLANES:
        for i in range(10):
            alias(start + i, ord("0") + i)

    # Letterlike-symbol holes.
    for cp, letter in _LETTERLIKE.items():
        alias(cp, ord(letter))

    # Greek letters.
    for cap_start, small_start in _GREEK_PLANES:
        for i, base_cp in enumerate(_GREEK_CAP_ORDER):
            alias(cap_start + i, base_cp)
        for i, base_cp in enumerate(_GREEK_SMALL_ORDER):
            alias(small_start + i, base_cp)

    return out
