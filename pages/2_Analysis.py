import streamlit as st

from app.sections.analysis.current_report import render_current_report_section
from app.sections.analysis.historical_reports import (
    render_historical_report_section,
)

st.title("Market Analysis")

# 1. Current Report
render_current_report_section()

st.write("")
st.write("")

# 2. Historical Archive
render_historical_report_section()
