from typing import List, Dict, Any, Union
import time

import pandas as pd
import streamlit as st

from summarizer.summarizer import Summarizer
from llm.llm import LLM
from ingestion.generate_ingest import IngestionGenerator
from utils.test_connection import test_database_connection

from st.components.introduction import introduction
from st.components.iterate_model import iterate_model
from st.components.iterate_model_input import iterate_model_input
from st.components.sidebar import sidebar
from st.components.csv_loader import csv_loader
from st.components.ingest import ingest

def neo4j_credentials_component(show: bool = True) -> None:
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
                        "database": database
                    }
                test_response = test_database_connection(credentials=credentials)
                if test_response["valid"]:
                    st.session_state["show_credentials"] = False 
                    st.session_state["NEO4J_CREDENTIALS"] = credentials
                    st.write(test_response["message"])
                else:
                    st.warning(test_response["message"])

def ingestion_generation_component(data_model: Dict[str, Any], show: bool = True) -> None:
    """
    Ingestion Generation Component. Allows options for which ingestion method
    the user prefers and download options.
    """

    st.session_state["ingestion_generator"] = IngestionGenerator(data_model=data_model,
                             username=st.session_state["NEO4J_CREDENTIALS"]["username"],
                             password=st.session_state["NEO4J_CREDENTIALS"]["password"],
                             uri=st.session_state["NEO4J_CREDENTIALS"]["uri"],
                             database=st.session_state["NEO4J_CREDENTIALS"]["database"]
                             )
    
    with st.expander(label="Data Ingestion", expanded=show):

        col1, col2, col3 = st.columns(3)

        with col1: 
            st.download_button(label="PyIngest", data="dummy", disabled=True)
        
        with col2:
            st.download_button(label="load_csv", data="dummy", disabled=False)

        with col3:
            st.download_button(label="constraints", data="dummy", disabled=False)

def discovery_component(show: bool = True) -> None:
    """
    Discovery component. Display the LLM discovery step.
    """

    with st.status("Discovery", expanded=st.session_state["show_discovery"]):
        if st.session_state["discovery_ran"] == False:
            st.session_state["discovery"] = st.session_state["summarizer"].run_discovery()
        st.write(st.session_state["discovery"])
        st.session_state["discovery_ran"] = True
        st.session_state["show_initial_data_model"] = True

def initial_model_component(show: bool = True) -> None:
    """
    Display the intial data model JSON and visual.
    """
    with st.status("Data Model V1", expanded=show):
        st.write("Creating Initial Data Model")

        # only run the first time!
        if st.session_state["initial_model_created"] == False:
            st.session_state["summarizer"].create_initial_model()
            # we iterate once to refine the first displayed model
            st.session_state["summarizer"].iterate_model(iterations=1)
            st.session_state["initial_model_created"] = True

        st.json(st.session_state["summarizer"].current_model, expanded=False)
        st.graphviz_chart(st.session_state["summarizer"].model_history[-1].visualize(), use_container_width=True)
                    
# ------------------
# ------------------
# ------------------

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
        "database": None
    }
    st.session_state["summarizer"] = None
    st.session_state["ingestion_code_generated"] = False
    st.session_state["model_iteration"] = 1

st.title("CSV --> Graph")

introduction(content_file_path="st/ui/intro.md")

neo4j_credentials_component(show=st.session_state["show_credentials"])

csv_loader(show=st.session_state["show_csv_loader"])

if st.session_state["user_input_gathered"] and st.session_state["summarizer"] is not None:   

    discovery_component(show=st.session_state["show_discovery"])

    initial_model_component(show=st.session_state["show_initial_data_model"])
    
    print("run iterate model before: ", st.session_state["run_iterate_model"])
    print("iteration: ", st.session_state['model_iteration'])
    if st.session_state["model_iteration"] > 1:
        iterate_model(show=st.session_state["show_iterate_model"])

    iterate_model_input(show=st.session_state["show_iterate_model_input"])
    
    # after user has confirmed model we show this content
    # ingestion_generation_component(data_model=st.session_state["summarizer"].model_history[-1].dict, 
    #                                show=st.session_state["show_ingestion"])

    ingest(show=st.session_state["show_ingestion"])
# generate sidebar last
sidebar(content_file_path="st/ui/sidebar.md")

    
    
    


        

            
        