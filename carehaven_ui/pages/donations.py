from __future__ import annotations
import streamlit as st
from carehaven_ui.api_client.client import ApiClient, ApiError
from carehaven_ui.api_client.donations import create_donation, my_donation_history
from carehaven_ui.components.navbar import render_navbar
def render() -> None:
    render_navbar("Donations")
    client = ApiClient(token=st.session_state.get("token"))
    try:
        response = my_donation_history(client)
        st.dataframe(response.get("items", []), use_container_width=True)
    except ApiError as exc: st.error(str(exc))
    with st.form("donation"):
        case_id, amount = st.text_input("Case ID"), st.number_input("Amount", min_value=0.01)
        submitted = st.form_submit_button("Record donation")
    if submitted:
        try: st.success(f"Donation recorded: {create_donation(client, {'case_id': case_id, 'amount': amount})}")
        except ApiError as exc: st.error(str(exc))
