from __future__ import annotations
import streamlit as st
from streamlit.components.navbar import render_navbar
def render() -> None:
    render_navbar("Review Queue")
    st.info("The published API list has no review-queue or approval endpoint. This page will become operational when the backend provides a documented endpoint and response schema.")
