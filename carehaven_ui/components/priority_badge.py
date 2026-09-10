from __future__ import annotations
def priority_badge(priority: str | None) -> str:
    """Return a compact Markdown label without changing backend priority values."""
    label = priority or "Unknown"
    color = {"Critical": "#b91c1c", "High": "#ea580c", "Medium": "#ca8a04", "Low": "#15803d"}.get(label, "#475569")
    return f"<span style='background:{color};color:white;padding:0.15rem 0.45rem;border-radius:0.3rem'>{label}</span>"
