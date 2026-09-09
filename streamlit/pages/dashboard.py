from __future__ import annotations
import streamlit as st
from streamlit.api_client.cases import list_cases
from streamlit.api_client.client import ApiClient, ApiError
from streamlit.components.case_card import render_case_card
from streamlit.components.charts import render_case_status_chart
from streamlit.components.navbar import render_navbar
def render() -> None:
    render_navbar("Dashboard")
    try:
        cases = list_cases(ApiClient(token=st.session_state.get("token")))
    except ApiError as exc: st.error(str(exc)); return
    cases = cases if isinstance(cases, list) else cases.get("items", [])
    active = [case for case in cases if case.get("status") == "Active"]
    urgent = [case for case in cases if case.get("priority") in {"High", "Critical"}]
    a, b, c = st.columns(3); a.metric("Total cases", len(cases)); b.metric("Active cases", len(active)); c.metric("High priority", len(urgent))
    st.subheader("Case status"); render_case_status_chart(cases)
    st.subheader("Recent cases")
    for case in cases[:5]: render_case_card(case)
