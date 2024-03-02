import streamlit as st

def column_input(column_name: str) -> None:
    """
    Input component for a column.
    """

    c1, c2, c3 = st.columns([0.25, 0.6, 0.15])
    with c1:
        st.text(body=column_name)
    with c2:
        st.session_state["USER_GENERATED_INPUT"][column_name] = st.text_input(label=column_name,
                                    label_visibility="collapsed",
                                    placeholder="column description...")
    with c3:
        ignore = st.checkbox(label="ignore", key=column_name+"-ignore-button", label_visibility="collapsed")
        if ignore:
            st.session_state["USER_GENERATED_INPUT"].pop(column_name)