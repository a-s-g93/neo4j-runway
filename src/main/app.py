from typing import List, Dict, Any, Union

import streamlit as st

from st.components.introduction import introduction
from st.components.neo4j_credentials import neo4j_credentials
from st.components.discovery import discovery
from st.components.initial_model import initial_model
from st.components.iterate_model import iterate_model
from st.components.user_corrections import user_corrections
from st.components.sidebar import sidebar
from st.components.csv_loader import csv_loader
from st.components.ingest import ingest

# init variables
if "user_input_gathered" not in st.session_state.keys():

    # USER INPUT FLAG
    st.session_state["user_input_gathered"] = False

    # EXPANDER FLAGS
    st.session_state["show_credentials"] = True
    st.session_state["show_csv_loader"] = True
    st.session_state["show_discovery"] = True
    st.session_state["show_initial_data_model"] = True
    st.session_state["show_iterate_model"] = False
    st.session_state["show_iterate_model_input"] = True
    st.session_state["show_ingestion"] = True

    # LLM FLAGS
    st.session_state["discovery_ran"] = False
    st.session_state["initial_model_created"] = False
    st.session_state["run_iterate_model"] = False

    # MISC
    st.session_state["NEO4J_CREDENTIALS"] = {
        "username": None,
        "password": None,
        "uri": None,
        "database": None,
    }
    st.session_state["summarizer"] = None
    st.session_state["ingestion_code_generated"] = False
    st.session_state["model_iteration"] = 1
    st.session_state["disable_ingest"] = True

st.title("Neo4j Runway | :green[beta]")

introduction(content_file_path="st/ui/intro.md")

neo4j_credentials(show=st.session_state["show_credentials"])

csv_loader(show=st.session_state["show_csv_loader"])

if (
    st.session_state["user_input_gathered"]
    and st.session_state["summarizer"] is not None
):
    print("Using LLM: ", st.session_state["model_name"])

    discovery(show=st.session_state["show_discovery"])

    initial_model(show=st.session_state["show_initial_data_model"])

    if st.session_state["model_iteration"] > 1:
        iterate_model(show=st.session_state["show_iterate_model"])

    user_corrections(show=st.session_state["show_iterate_model_input"])

    ingest(show=st.session_state["show_ingestion"])

# generate sidebar last
sidebar(content_file_path="st/ui/sidebar.md")
