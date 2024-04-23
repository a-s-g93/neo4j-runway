import streamlit as st

from ingestion.generate_ingest import IngestionGenerator
from neo4j_runway.main.ingestion.pyingest import PyIngestForStreamlit


def ingest(show: bool = True) -> None:
    """
    Give options for data ingestion via the application.
    """

    with st.expander("Ingest", expanded=show):

        st.write("Ingest the CSV data into the linked Neo4j database.")

        with st.form(key="data-model-version-select-pyingest-ingestion"):
            current_model_version = (
                len(st.session_state["summarizer"].model_history) - 1
            )
            version = st.number_input(
                label="Select Data Model Version",
                min_value=1,
                max_value=current_model_version,
                placeholder=current_model_version,
            )

            if st.form_submit_button(
                label="Ingest",
                disabled=st.session_state["disable_ingest"],
                help="Neo4j credentials required.",
            ):

                gen_temp = IngestionGenerator(
                    data_model=st.session_state["summarizer"]
                    .model_history[version]
                    .dict,
                    username=st.session_state["NEO4J_CREDENTIALS"]["username"],
                    password=st.session_state["NEO4J_CREDENTIALS"]["password"],
                    uri=st.session_state["NEO4J_CREDENTIALS"]["uri"],
                    database=st.session_state["NEO4J_CREDENTIALS"]["database"],
                    csv_name=st.session_state["csv_name"],
                    csv_dir="",
                    file_output_dir="",
                )

                yaml = gen_temp.generate_pyingest_yaml_string()
                # PyIngest(yaml_string=yaml)
                # st.write(yaml)
                prog_bar = st.progress(value=0.0, text="Ingesting...")
                for prog in PyIngestForStreamlit(
                    yaml_string=yaml, dataframe=st.session_state["dataframe"]
                ):
                    prog_bar.progress(value=prog, text="Ingesting...")
                prog_bar.progress(value=prog, text="Ingestion Complete!")
                st.session_state["disable_ingest"] = True

        # if st.button(label="Ingest", key="ingest-key"):
        #     st.write("Ingesting!")
