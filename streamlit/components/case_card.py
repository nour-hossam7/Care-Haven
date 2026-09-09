from __future__ import annotations
from typing import Any
import streamlit as st
from .priority_badge import priority_badge
from .status_badge import status_badge
def render_case_card(case: dict[str, Any]) -> None:
    """Render a case response safely despite optional backend fields."""
    with st.container(border=True):
        st.subheader(str(case.get("title") or case.get("case_id") or "Case"))
        st.caption(f"{case.get('location') or case.get('city') or 'Location unavailable'} · {case.get('submission_date', '')}")
        st.markdown(f"{priority_badge(case.get('priority'))} &nbsp; {status_badge(case.get('status'))}", unsafe_allow_html=True)
        if case.get("description"): st.write(case["description"])
        if st.button("View details", key=f"case-{case.get('case_id')}"): st.session_state.selected_case_id = case.get("case_id")
