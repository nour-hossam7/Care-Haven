from __future__ import annotations
import streamlit as st
from ai.vision.quality import assess_image_quality
from streamlit.api_client.cases import create_case
from streamlit.api_client.client import ApiClient, ApiError
from streamlit.components.navbar import render_navbar
def render() -> None:
    render_navbar("Submit a case")
    with st.form("submit-case"):
        description = st.text_area("Description")
        location = st.text_input("Location")
        people = st.number_input("People affected", min_value=1, step=1)
        assistance = st.text_input("Required assistance (comma-separated)")
        amount = st.number_input("Required amount", min_value=0.0)
        image = st.file_uploader("Evidence image (validated locally; upload API contract unavailable)", type=["jpg", "jpeg", "png", "webp"])
        submitted = st.form_submit_button("Submit")
    if image:
        quality = assess_image_quality(image.getvalue()); st.image(image); st.write("Image quality", quality)
    if submitted:
        if not description or not location or not assistance or amount <= 0: st.error("Complete all required fields with a positive amount."); return
        payload = {"description": description, "location": location, "people_affected": int(people), "required_assistance": [value.strip() for value in assistance.split(",") if value.strip()], "required_amount": amount}
        try: st.success(f"Case submitted: {create_case(ApiClient(token=st.session_state.get('token')), payload)}")
        except ApiError as exc: st.error(str(exc))
