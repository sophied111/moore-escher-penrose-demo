"""Curated (prompt, seed, family) rows for gr.Examples — the gallery + prompt teacher."""

FAMILIES = ["conformal", "poles", "mobius", "square", "rimrings"]

EXAMPLES = [
    [
        "A photorealistic old map spread on a wooden table; an explorer drawn in "
        "ink walks off the edge of the map onto the real table, and the map "
        "depicts this same table, map, and walking explorer; candle light, "
        "parchment texture, ink turning into cloth.",
        7,
        "conformal",
    ],
    [
        "A photorealistic gallery whose far wall is a photo of the same gallery, "
        "no text.",
        100,
        "conformal",
    ],
    [
        "A photorealistic artist's desk with an open comic page; the inked "
        "character steps out of its panel into full photographic reality on the "
        "desk, the page still showing this same desk and the same stepping "
        "character; drafting lamp, halftone dots resolving into real fabric.",
        1234,
        "conformal",
    ],
]
