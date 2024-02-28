import streamlit as st

def introduction(content_file_path: str) -> None:
    """
    Display introduction content.
    """

    with open(content_file_path, "r") as intro_file:
        intro_content = intro_file.read()

    st.markdown(intro_content)