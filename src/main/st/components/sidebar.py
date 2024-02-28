import json
from typing import Dict

import streamlit as st

from ingestion.generate_ingest import IngestionGenerator

def sidebar(content_file_path: str) -> None:
    """
    The sidebar component.
    Contains download options for generated deliverables.
    """

    with open(content_file_path, "r") as f:
        content = f.read()

    st.sidebar.markdown(content)

    if st.session_state["summarizer"] is not None:
        with st.sidebar.form("Data Model Version Select"):
            current_model_version = len(st.session_state["summarizer"].model_history)-1
            version = st.number_input(label="Select Data Model Version", min_value=1, max_value=current_model_version, placeholder=current_model_version)

            if st.form_submit_button("Generate Ingestion Code"):

                st.session_state["ingestion_generator"] = IngestionGenerator(data_model=st.session_state["summarizer"].model_history[version-1].dict,
                                        username=st.session_state["NEO4J_CREDENTIALS"]["username"],
                                        password=st.session_state["NEO4J_CREDENTIALS"]["password"],
                                        uri=st.session_state["NEO4J_CREDENTIALS"]["uri"],
                                        database=st.session_state["NEO4J_CREDENTIALS"]["database"]
                                        )
                st.session_state["ingestion_code_generated"] = True

        
        st.sidebar.download_button(
                label=f"Data Model V{str(version)}",
                data=json.dumps(st.session_state["summarizer"].model_history[version-1].dict),
                file_name=f'data_model_v{str(version)}.json',
                mime='application/json',
            )
        if st.session_state["ingestion_code_generated"]:      
            disable_pyingest = False
            if st.session_state["NEO4J_CREDENTIALS"]['username'] is None:
                disable_pyingest = True

            pyingest_string = get_pyingest_file(file_name=f"pyingest_config_data_model_v{str(version)}")
            st.sidebar.download_button(
                label="PyIngest Yaml",
                data=pyingest_string,
                file_name=f'pyingest_config_data_model_v{str(version)}.yml',
                mime='text/plain',
                disabled=disable_pyingest
            )
        
            load_csv_string = get_load_csv_file(file_name=f"load_csv_data_model_v{str(version)}")
            st.sidebar.download_button(
                label="load_csv",
                data=load_csv_string,
                file_name=f'load_csv.cypher_data_model_v{str(version)}',
                mime='text/plain',
            )

            constraints_string = get_constraints_cypher_file(file_name=f"constraints_data_model_v{str(version)}")
            st.sidebar.download_button(
                label="Constraints",
                data=constraints_string,
                file_name=f"constraints_data_model_v{str(version)}",
                mime='text/plain',
            )

@st.cache_data
def get_pyingest_file(file_name: str):
    return st.session_state["ingestion_generator"].generate_pyingest_yaml(write_file=False)

@st.cache_data
def get_load_csv_file(file_name: str):
    return st.session_state["ingestion_generator"].generate_load_csv(write_file=False)


@st.cache_data
def get_constraints_cypher_file(file_name: str):
    return st.session_state["ingestion_generator"].generate_constraints_cypher(write_file=False)

