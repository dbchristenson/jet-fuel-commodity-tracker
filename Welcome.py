import streamlit as st

from app.sections.header import render_header

st.set_page_config(
    page_title="JetDash",
    page_icon="🦅",
)

st.write("# Welcome to Jet Dash! 🦅")

st.markdown(
    """
    JetDash is an interactive dashboard for tracking
    **U.S. Gulf Coast Kerosene-Type Jetfuel**. Explore commodity prices,
    refinery data, current events, and our own analyst's price predictions.

    ### How to use this app
    To get started, select a page from the sidebar on the left.
    - The **Dashboard** page contains visualizations of commodity prices,
    refinery data, current events, and price predictions.
    - The **Analysis** page contains insights on our team's expectations for
    the jet fuel market week to week.
    """
)

st.sidebar.success("Select a page to view above.")

render_header()
