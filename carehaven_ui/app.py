"""CareHaven Streamlit application entry point."""
from __future__ import annotations
import streamlit as st
from carehaven_ui.config import settings
from carehaven_ui.components.sidebar import choose_page
from carehaven_ui.pages import ai_assistant, case_details, cases, dashboard, donations, image_analysis, login, map as map_page, recommendations, review_queue, submit_case

ROUTES = {"Dashboard": dashboard, "Cases": cases, "Submit Case": submit_case, "Donations": donations, "Recommendations": recommendations, "AI Assistant": ai_assistant, "Image Analysis": image_analysis, "Review Queue": review_queue, "Map": map_page}

def main() -> None:
    st.set_page_config(page_title=settings.app_title, page_icon="♥", layout="wide")
    st.session_state.setdefault("authenticated", False)
    if not st.session_state.authenticated:
        login.render(); return
    page = choose_page()
    if st.session_state.get("selected_case_id") and page == "Cases": case_details.render()
    else: ROUTES[page].render()

if __name__ == "__main__": main()
