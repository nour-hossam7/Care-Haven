from __future__ import annotations
import streamlit as st
from carehaven_ui.api_client.cases import list_cases
from carehaven_ui.api_client.client import ApiClient, ApiError
from carehaven_ui.components.case_card import render_case_card
from carehaven_ui.components.navbar import render_navbar
def render() -> None:
    render_navbar("Cases")
    try: response = list_cases(ApiClient(token=st.session_state.get("token")))
    except ApiError as exc: st.error(str(exc)); return
    cases = response if isinstance(response, list) else response.get("items", [])
    priorities = sorted({str(item.get("priority")) for item in cases if item.get("priority")})
    selected = st.multiselect("Priority", priorities)
    for case in cases:
        if not selected or case.get("priority") in selected: render_case_card(case)
