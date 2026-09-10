from __future__ import annotations
from typing import Any
import streamlit as st
def render_case_status_chart(cases: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    for case in cases: counts[str(case.get("status", "Unknown"))] = counts.get(str(case.get("status", "Unknown")), 0) + 1
    if counts: st.bar_chart(counts)
