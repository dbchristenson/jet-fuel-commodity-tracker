import streamlit as st

from app.sections.commodity import render_commodity_section
from app.sections.header import render_header
from app.sections.news import render_news_section

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
render_news_section()
st.caption(
    "Powered by Argus Media",
    help="Argus Media provides news and analysis on commodity markets.",
    text_alignment="right",
)

# -----------------------------------------------------------------------------
# LLM Prediction Section (llm_prediction.py)
# Powered by Gemini
# -----------------------------------------------------------------------------
st.header("Jet Fuel Price Prediction", divider="gray")
st.caption("Powered by Gemini", text_alignment="right")

# -----------------------------------------------------------------------------
# Jet Fuel Team Prediction Section (team_prediction.py)
# -----------------------------------------------------------------------------
st.header("Human Price Prediction", divider="gray")
st.caption("Powered by Brains", help="", text_alignment="right")

# -----------------------------------------------------------------------------
# Footer Section (footer.py)
# -----------------------------------------------------------------------------
