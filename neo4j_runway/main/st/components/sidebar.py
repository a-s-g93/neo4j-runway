import io
import json
from typing import Dict
import zipfile

import streamlit as st

from ingestion.generate_ingest import IngestionGenerator


def sidebar(content_file_path: str) -> None:
    """
    The sidebar component.
    Contains download options for generated deliverables.
    """

    with open(content_file_path, "r") as f:
        content = f.read()

    if st.session_state["summarizer"] is None:
        disable_model_select = False
    else:
        disable_model_select = True
    st.session_state["model_name"] = st.sidebar.radio(
        "Select LLM",
        ["gpt-4-0125-preview", "gpt-3.5-turbo"],
        disabled=disable_model_select,
    )
    st.sidebar.markdown(content)

    if st.session_state["summarizer"] is not None:
        with st.sidebar.form("Data Model Version Select"):
            csv_dir = st.text_input(
                label="Local CSV Location",
                value="./",
                placeholder="where is this file found?",
            )
            # file_output_dir = st.text_input(label="")
            current_model_version = (
                len(st.session_state["summarizer"].model_history) - 1
            )
            version = st.number_input(
                label="Select Data Model Version",
                min_value=1,
                max_value=current_model_version,
                placeholder=current_model_version,
            )

            if st.form_submit_button("Generate Ingestion Code"):

                st.session_state["ingestion_generator"] = IngestionGenerator(
                    data_model=st.session_state["summarizer"]
                    .model_history[version]
                    .dict,
                    username=st.session_state["NEO4J_CREDENTIALS"]["username"],
                    password=st.session_state["NEO4J_CREDENTIALS"]["password"],
                    uri=st.session_state["NEO4J_CREDENTIALS"]["uri"],
                    database=st.session_state["NEO4J_CREDENTIALS"]["database"],
                    csv_name=st.session_state["csv_name"],
                    csv_dir=csv_dir,
                    file_output_dir="",
                )
                st.session_state["ingestion_code_generated"] = True

        st.sidebar.download_button(
            label=f"Data Model V{str(version)}",
            data=json.dumps(
                st.session_state["summarizer"].model_history[version].model_dump()
            ),
            file_name=f"data_model_v{str(version)}.json",
            mime="application/json",
            help="The selected data model in JSON format.",
        )
        if st.session_state["ingestion_code_generated"]:
            # disable_pyingest = False
            # if st.session_state["NEO4J_CREDENTIALS"]['username'] is None:
            #     disable_pyingest = True

            pyingest_string = prepare_pyingest()
            st.sidebar.download_button(
                label="PyIngest Yaml",
                data=pyingest_string,
                file_name=f"pyingest_config_data_model_v{str(version)}.yml",
                mime="text/plain",
                # disabled=disable_pyingest,
                help="PyIngest yaml file.",
            )

            load_csv_string = prepare_load_csv()
            st.sidebar.download_button(
                label="load_csv",
                data=load_csv_string,
                file_name=f"load_csv_cypher_data_model_v{str(version)}.cypher",
                mime="text/plain",
                help="load_csv cypher file.",
            )

            constraints_string = prepare_constraints()
            st.sidebar.download_button(
                label="Constraints",
                data=constraints_string,
                file_name=f"constraints_data_model_v{str(version)}.cypher",
                mime="text/plain",
                help="Constraints file containing unique constraints.",
            )
            st.sidebar.divider()
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "x") as zip:
                zip.writestr(
                    f"data_model_v{str(version)}.json",
                    json.dumps(
                        st.session_state["summarizer"]
                        .model_history[version]
                        .model_dump()
                    ),
                )
                zip.writestr(
                    f"pyingest_config_data_model_v{str(version)}.yml", pyingest_string
                )
                zip.writestr(
                    f"load_csv_cypher_data_model_v{str(version)}.cypher",
                    load_csv_string,
                )
                zip.writestr(
                    f"constraints_data_model_v{str(version)}.cypher", constraints_string
                )

            st.sidebar.download_button(
                label="All Files",
                data=buf.getvalue(),
                file_name="runway_package.zip",
                mime="application/zip",
                use_container_width=True,
                # type="primary",
                help="Download all files.",
            )


@st.cache_data
def prepare_pyingest():
    return st.session_state["ingestion_generator"].generate_pyingest_yaml_string()


@st.cache_data
def prepare_load_csv():
    return st.session_state["ingestion_generator"].generate_load_csv_string()


@st.cache_data
def prepare_constraints():
    return st.session_state["ingestion_generator"].generate_constraints_cypher_string()
