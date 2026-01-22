import streamlit as st

from app.sections.commodity import render_commodity_section
from app.sections.news import render_news_section
from app.sections.refinery import render_refinery_section

st.set_page_config(
    page_title="Dashboard",
    page_icon=":earth_americas:",
)

# -----------------------------------------------------------------------------
# Navigation Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    ## Index
    1. Jet Fuel & Other Middle Distillates Spot Prices
    2. US Refinery Utilization Rates for Relevant Products
    3. Jet Fuel Current Events and News
    4. Jet Fuel Price Prediction (LLM)
    5. Human Price Prediction
    """
)


# -----------------------------------------------------------------------------
# Commodity Price Visualization Section (commodity.py)
# -----------------------------------------------------------------------------
render_commodity_section()

# -----------------------------------------------------------------------------
# Refinery Section (refinery.py)
# -----------------------------------------------------------------------------
render_refinery_section()

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
st.caption(
    "Powered by Gemini",
    help="Gemini is fed quantitative data, current events, and jet-fuel specific news to inform its prediction. This application uses the Gemini Flash 3 model.",  # noqa E501
    text_alignment="right",
)

# -----------------------------------------------------------------------------
# Jet Fuel Team Prediction Section (team_prediction.py)
# -----------------------------------------------------------------------------
st.header("Human Price Prediction", divider="gray")
st.caption("Powered by Brains", help="", text_alignment="right")

# -----------------------------------------------------------------------------
# Footer Section (footer.py)
# -----------------------------------------------------------------------------
