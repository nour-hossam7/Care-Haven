from __future__ import annotations
import streamlit as st
from streamlit.api_client.cases import list_review_queue, update_evidence_verification
from streamlit.api_client.client import ApiClient, ApiError
from streamlit.components.navbar import render_navbar
def render() -> None:
    render_navbar("Review Queue")
    client = ApiClient(token=st.session_state.get("token"))
    try:
        queue = list_review_queue(client)
    except ApiError as exc:
        st.error(str(exc))
        return
    items = queue.get("items", [])
    if not items:
        st.info("There is no unreviewed evidence.")
        return
    for evidence in items:
        st.subheader(f"Evidence {evidence['evidence_id']}")
        st.write(f"Case: {evidence['case_id']} | Status: {evidence['verification_status']}")
        if evidence.get("description"):
            st.write(evidence["description"])
        st.caption(evidence.get("file_path") or "Image path unavailable")
        approve, reject = st.columns(2)
        for label, decision, column in (("Approve", "approved", approve), ("Reject", "rejected", reject)):
            if column.button(label, key=f"{decision}-{evidence['evidence_id']}"):
                try:
                    update_evidence_verification(client, evidence["evidence_id"], decision)
                    st.rerun()
                except ApiError as exc:
                    st.error(str(exc))
