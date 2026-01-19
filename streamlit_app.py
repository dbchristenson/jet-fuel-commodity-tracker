import streamlit as st

from app.sections.commodity import render_commodity_section
from app.sections.header import render_header

# -----------------------------------------------------------------------------
# Header Section (header.py)
# -----------------------------------------------------------------------------
render_header()

# -----------------------------------------------------------------------------
# Commodity Price Visualization Section (commodity.py)
# -----------------------------------------------------------------------------
render_commodity_section()

# -----------------------------------------------------------------------------
# Refinery Section (refinery.py)
# -----------------------------------------------------------------------------
st.header("US Refinery Utilization Rates", divider="gray")

# -----------------------------------------------------------------------------
# News Section (news.py)
# Powered by Argus Media
# -----------------------------------------------------------------------------
st.header("Jet Fuel Current Events and News", divider="gray")
st.caption(
    "Powered by Argus Media",
    help="Argus Media provides news and analysis on commodity markets.",
)

# -----------------------------------------------------------------------------
# LLM Prediction Section (llm_prediction.py)
# Powered by Gemini
# -----------------------------------------------------------------------------
st.header("Jet Fuel Price Prediction", divider="gray")
st.caption("Powered by Gemini")

# -----------------------------------------------------------------------------
# Jet Fuel Team Prediction Section (team_prediction.py)
