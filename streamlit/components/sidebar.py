from __future__ import annotations
import streamlit as st
PAGES = ["Dashboard", "Cases", "Submit Case", "Donations", "Recommendations", "AI Assistant", "Image Analysis", "Review Queue", "Map"]
def choose_page() -> str:
    """Show simple centralized navigation; backend roles remain authoritative."""
    return st.sidebar.radio("Navigate", PAGES)
