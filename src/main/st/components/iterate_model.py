

import streamlit as st


def iterate_model(show: bool = False) -> None:
    """
    Produces an updated model.
    """
    print("internal show: ", show)
    iteration = st.session_state["model_iteration"]
    with st.status(f"Data Model V{iteration}", expanded=show):

        if st.session_state["run_iterate_model"]:
            print(f"running iterate {iteration}...")
            st.session_state["summarizer"].iterate_model(iterations=1)
            st.session_state["run_iterate_model"] = False

        st.json(st.session_state["summarizer"].current_model, expanded=False)
        st.graphviz_chart(st.session_state["summarizer"].model_history[-1].visualize(), use_container_width=True)