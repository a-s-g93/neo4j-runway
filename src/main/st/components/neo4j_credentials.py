import streamlit as st

from utils.test_connection import test_database_connection


def neo4j_credentials(show: bool = True) -> None:
    """
    Component to handle Neo4j credentials submission.
    """

    with st.expander("Neo4j Credentials", expanded=show):
        with st.form("Neo4j-credentials-form", clear_on_submit=True):
            uri = st.text_input(label="uri")
            database = st.text_input(label="database", value="neo4j")
            username = st.text_input(label="Username", value="neo4j")
            password = st.text_input(label="Password", type="password")

            submitted = st.form_submit_button("Link Database")
            if submitted:
                credentials = {
                    "uri": uri,
                    "username": username,
                    "password": password,
                    "database": database,
                }
                test_response = test_database_connection(credentials=credentials)
                if test_response["valid"]:
                    st.session_state["show_credentials"] = False
                    st.session_state["NEO4J_CREDENTIALS"] = credentials
                    st.write(test_response["message"])
                    st.session_state["disable_ingest"] = False
                else:
                    st.warning(test_response["message"])
