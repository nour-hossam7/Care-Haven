from __future__ import annotations
import streamlit as st
from carehaven_ui.api_client.auth import login
from carehaven_ui.api_client.client import ApiClient, ApiError
def render() -> bool:
    st.title("Care-Haven")
    st.caption("Sign in to access humanitarian cases and tools.")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")
    if submitted:
        try:
            result = login(ApiClient(), email, password)
            token = result.get("access_token") or result.get("token")
            if not token: raise ApiError("The login response did not include an access token.")
            if str(result.get("token_type", "bearer")).lower() != "bearer": raise ApiError("The login response used an unsupported token type.")
            st.session_state.update(authenticated=True, token=token, user=result.get("user", {}))
            st.rerun()
        except ApiError as exc: st.error(str(exc))
    return False
