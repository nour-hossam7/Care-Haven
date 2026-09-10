from __future__ import annotations
def status_badge(status: str | None) -> str:
    label = status or "Unknown"
    color = {"Active": "#2563eb", "Under Review": "#a16207", "Funded": "#15803d", "Completed": "#475569"}.get(label, "#475569")
    return f"<span style='background:{color};color:white;padding:0.15rem 0.45rem;border-radius:0.3rem'>{label}</span>"
