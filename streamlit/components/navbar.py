from __future__ import annotations
import streamlit as st
def render_navbar(page_title: str) -> None:
    left, right = st.columns([4, 1])
    with left: st.title(f"Care-Haven · {page_title}")
    with right:
        user = st.session_state.get("user", {})
        if user: st.caption(str(user.get("email") or user.get("name") or "Signed in"))
        if user and st.button("Log out", key="logout"):
            for key in ("token", "user", "authenticated"): st.session_state.pop(key, None)
            st.rerun()
