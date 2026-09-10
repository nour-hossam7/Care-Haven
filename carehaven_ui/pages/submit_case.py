from __future__ import annotations
import streamlit as st
from ai.vision.quality import assess_image_quality
from carehaven_ui.api_client.cases import create_case, upload_evidence
from carehaven_ui.api_client.client import ApiClient, ApiError
from carehaven_ui.components.navbar import render_navbar
def render() -> None:
    render_navbar("Submit a case")
    with st.form("submit-case"):
        description = st.text_area("Description")
        assistance_category = st.text_input("Assistance category")
        people = st.number_input("People affected", min_value=1, step=1)
        country = st.text_input("Country")
        governorate = st.text_input("Governorate (optional)")
        city = st.text_input("City (optional)")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
        resources = st.text_input("Required resources (optional)")
        amount = st.number_input("Estimated funding (optional)", min_value=0.0)
        image = st.file_uploader("Evidence image (validated locally)", type=["jpg", "jpeg", "png", "webp"])
        submitted = st.form_submit_button("Submit")
    if image:
        quality = assess_image_quality(image.getvalue()); st.image(image); st.write("Image quality", quality)
    if submitted:
        if not description or not assistance_category or not country: st.error("Complete all required fields."); return
        payload = {"description": description, "assistance_category": assistance_category, "people_affected": int(people), "country": country, "severity": severity, "urgency": urgency}
        if governorate: payload["governorate"] = governorate
        if city: payload["city"] = city
        if resources: payload["required_resources"] = resources
        if amount > 0: payload["estimated_funding"] = amount
        try:
            client = ApiClient(token=st.session_state.get("token"))
            case = create_case(client, payload)
            st.success(f"Case submitted: {case.get('case_id', 'created')}")
            if image:
                try:
                    upload_evidence(
                        client,
                        case["case_id"],
                        (image.name, image.getvalue(), image.type or "image/jpeg"),
                        description=description,
                    )
                    st.success("Evidence image uploaded and queued for review.")
                except ApiError as exc:
                    st.error(
                        "The case was created, but its evidence image could not be uploaded. "
                        f"{exc}"
                    )
                except KeyError:
                    st.error(
                        "The case was created, but the server did not return a case ID for the evidence upload."
                    )
        except ApiError as exc: st.error(str(exc))
