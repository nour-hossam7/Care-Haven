from __future__ import annotations
from typing import Any
import streamlit as st
from streamlit.api_client.cases import list_cases
from streamlit.api_client.client import ApiClient, ApiError
from streamlit.components.navbar import render_navbar
def render() -> None:
    render_navbar("Case Map")
    try: response = list_cases(ApiClient(token=st.session_state.get("token")))
    except ApiError as exc: st.error(str(exc)); return
    cases: list[dict[str, Any]] = response if isinstance(response, list) else response.get("items", [])
    points = []
    for case in cases:
        try: points.append({"lat": float(case["latitude"]), "lon": float(case["longitude"])})
        except (KeyError, TypeError, ValueError): continue
    if points: st.map(points)
    else: st.info("No valid case coordinates are available.")
