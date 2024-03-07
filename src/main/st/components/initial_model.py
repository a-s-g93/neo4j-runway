import streamlit as st

def initial_model(show: bool = True) -> None:
    """
    Display the intial data model JSON and visual.
    """
    with st.status("Data Model V1", expanded=show):

        # only run the first time!
        if st.session_state["initial_model_created"] == False:
            st.session_state["summarizer"].create_initial_model()
            # we iterate once to refine the first displayed model
            st.session_state["summarizer"].iterate_model(iterations=1)
            st.session_state["initial_model_created"] = True

        st.json(st.session_state["summarizer"].model_history[1].dict, expanded=False)
        st.graphviz_chart(st.session_state["summarizer"].model_history[1].visualize(), use_container_width=True)