from __future__ import annotations
import streamlit as st
from streamlit.api_client.cases import get_case
from streamlit.api_client.client import ApiClient, ApiError
from streamlit.components.navbar import render_navbar
def render() -> None:
    render_navbar("Case details")
    case_id = st.session_state.get("selected_case_id") or st.text_input("Case ID")
    if not case_id: st.info("Choose a case from the Cases page."); return
    try: case = get_case(ApiClient(token=st.session_state.get("token")), str(case_id))
    except ApiError as exc: st.error(str(exc)); return
    st.json(case)
