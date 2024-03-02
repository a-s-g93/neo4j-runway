import os
import pandas as pd
import streamlit as st

from st.components.column_input import column_input
from summarizer.summarizer import Summarizer
from llm.llm import LLM

def csv_loader(show: bool = True) -> None:
    """
    Component for loading user csvs and receiving descriptions.
    """

    with st.expander("CSV Loader", expanded=show):
        openai_key = st.text_input(label="OpenAI API Key", placeholder="Key required for application.")
        csv_input = st.file_uploader(label="CSV Loader", accept_multiple_files=False, label_visibility="collapsed")

        if csv_input is not None:
            print("csv_type: ", type(csv_input))
            input_dataframe = pd.read_csv(csv_input)
            st.session_state["show_csv_loader"] = False
            st.session_state["csv_name"] = csv_input.name
            st.session_state["dataframe"] = input_dataframe


            # if "columns_of_interest" not in st.session_state.keys():
            st.session_state["columns_of_interest"] = list(input_dataframe.columns)

            with st.form("Columns Form"):
                
                st.write("""
                        Provide a description for each column you wish to include in the data model.\n
                        Select Ignore to ignore the column in the data model.
                        """)
                if "USER_GENERATED_INPUT" not in st.session_state.keys():
                    st.session_state["USER_GENERATED_INPUT"] = {}
                
                c1_gen, c2_gen = st.columns([0.3, 0.7])
                with c1_gen:
                    st.text(body="General Description")
                with c2_gen:
                    st.session_state["USER_GENERATED_INPUT"]["General Description"] = st.text_input(label="General Description", 
                                                                                                    label_visibility="collapsed", 
                                                                                                    placeholder="general description of the data...")

                c1, c2, c3 = st.columns([0.25, 0.6, 0.15])
                with c1:
                    st.subheader("Column")
                with c2:
                    st.subheader("Description")
                with c3:
                    st.subheader("Ignore")

                for col in st.session_state["columns_of_interest"]:
                    column_input(column_name=col)

                submitted = st.form_submit_button("Submit")
                openai_key = os.getenv('OPENAI_API_KEY') or openai_key
                if submitted and openai_key != "":
                    
                    st.session_state["user_input_gathered"] = True
                    # st.session_state["show_discovery"] = True
                    # st.session_state["show_initial_data_model"] = True
                    st.write(st.session_state["USER_GENERATED_INPUT"])
                    st.session_state["summarizer"] = Summarizer(llm=LLM(open_ai_key=openai_key), 
                                            user_input=st.session_state["USER_GENERATED_INPUT"], 
                                            data=input_dataframe)
                elif openai_key == "":
                    st.error("OpenAI API required to continue.")
                    st.stop()
     