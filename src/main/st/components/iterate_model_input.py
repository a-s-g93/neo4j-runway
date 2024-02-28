import streamlit as st

from summarizer.summarizer import Summarizer

def iterate_model_input(show: bool = True) -> None:
    """
    Receives user input to inject into the iterate model prompt.
    """

    with st.status("Iterate Model Input", expanded=show):

        user_input = st.text_input(label="Data Model Corrections", placeholder="Are there any corrections?")

        if st.button("Retry"):
            print("retrying model")
            st.session_state["model_iteration"]+=1
            st.session_state["run_iterate_model"] = True
            st.session_state["show_iterate_model"] = True
            st.rerun()
