from __future__ import annotations
import streamlit as st
from streamlit.api_client.chat import ask
from streamlit.api_client.client import ApiClient, ApiError
from streamlit.components.navbar import render_navbar
def render() -> None:
    render_navbar("AI Assistant")
    for message in st.session_state.setdefault("chat_messages", []):
        with st.chat_message(message["role"]): st.write(message["content"])
    if question := st.chat_input("Ask about humanitarian assistance"):
        st.session_state.chat_messages.append({"role": "user", "content": question})
        try:
            response = ask(ApiClient(token=st.session_state.get("token")), question)
            answer = str(response.get("answer") or response.get("response") or response)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer}); st.rerun()
        except ApiError as exc: st.error(str(exc))
