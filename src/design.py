"""Visual tokens from the team's UI guide; no Streamlit dependency."""

from hashlib import sha256

FONT_STACK = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
LIGHT_PALETTE = dict(
    bg="#F8FAFC", surface="#FFFFFF", text="#0F172A", muted="#475569",
    tertiary="#64748B", brand="#1E2E3B", border="#E2E8F0", action="#157A56",
    hover="#106144", soft="#EBF5F2", blue="#294A6B", link="#157A56",
)
# Categorical sentiment colors deliberately do not encode operational states.
CATEGORY_TONES = {
    "green": ("#D8E6D6", "#2D5A36"), "sand": ("#F4E3C9", "#7C5318"),
    "blue": ("#D6E2EE", "#294A6B"), "purple": ("#E2D9EE", "#4B326B"),
    "teal": ("#D1EAE5", "#1B5E52"),
    "slate": ("#E2E8F0", "#334155"),
    "rose": ("#EEDDE3", "#743A50"), "olive": ("#E5E8CF", "#515B27"),
}
CATEGORY_PALETTES = {
    "source": dict(mastodon="purple", hackernews="sand", stackoverflow="blue"),
    "theme": {
        "artificial-intelligence": "purple", "docker": "blue", "frontend": "teal",
        "backend": "green", "devops": "slate", "mobile": "sand",
        "machine-learning": "rose", "job": "olive",
    },
    "editorial": dict(success_case="green", faq="blue", newsletter="purple", moderation="sand", discard="slate", other="olive", fallback="teal", **{"Sem classificação": "slate"}),
    "sentiment": dict(Excited="purple", Happy="sand", Neutral="green", Disappointed="blue", Angry="teal", **{"Sem avaliação": "slate"}),
}
OPERATIONAL_TONES = {
    "success": ("#E8F5EE", "#157A56"), "info": ("#EAF1FB", "#1E4E8C"),
    "warning": ("#FFF3D6", "#76500D"), "error": ("#FDECEC", "#9C3038"),
}


def category_tone(dimension, value):
    """A value's color is independent of hierarchy, filtering and other values."""
    value = str(value)
    tone = CATEGORY_PALETTES.get(dimension, {}).get(value)
    if tone is None:
        names = tuple(CATEGORY_TONES)
        index = int.from_bytes(sha256(f"{dimension}:{value}".encode()).digest()[:4], "big")
        tone = names[index % len(names)]
    return CATEGORY_TONES[tone]

SANKEY_DEFAULT_COLOR = "#64748b"
SANKEY_SOURCE_COLORS = {"mastodon": "#293943", "hackernews": "#2DAC8A", "stackoverflow": "#47758A"}
SANKEY_NODE_COLORS = {
    "source": SANKEY_SOURCE_COLORS,
    "sentiment": {"Excited": "#7c3aed", "Happy": "#16a34a", "Neutral": "#94a3b8", "Disappointed": "#f59e0b", "Angry": "#dc2626"},
}
SANKEY_LEVEL_COLORS = {
    "theme": "#7c3aed",
    "editorial": "#0d9488",
}
