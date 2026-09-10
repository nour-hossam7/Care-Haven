from __future__ import annotations
import streamlit as st
from carehaven_ui.api_client.client import ApiClient, ApiError
from carehaven_ui.api_client.recommendations import recommendations_for
from carehaven_ui.components.case_card import render_case_card
from carehaven_ui.components.navbar import render_navbar
def render() -> None:
    render_navbar("Recommendations")
    donor_id = st.text_input("Donor ID")
    if donor_id and st.button("Get recommendations"):
        try:
            results = recommendations_for(ApiClient(token=st.session_state.get("token")), donor_id)
            for item in results: render_case_card(item)
        except ApiError as exc: st.error(str(exc))
