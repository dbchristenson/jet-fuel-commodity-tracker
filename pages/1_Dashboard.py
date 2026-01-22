import streamlit as st

from app.sections.commodity import render_commodity_section
from app.sections.llm_prediction import render_llm_section
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
    4. Market Analysis by John the Eagle (LLM)
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
st.header("John the Eagle Market Analysis", divider="gray")
render_llm_section()
st.caption(
    "Powered by Gemini",
    help="Gemini is fed quantitative data, current events, and jet-fuel specific news to inform its prediction. This application uses the Gemini Flash 3 model.",  # noqa E501
    text_alignment="right",
)

# -----------------------------------------------------------------------------
# Link to Human Analysis Page
# -----------------------------------------------------------------------------
st.markdown(
    """
    ---
    ## Want to see our human analyst's take?
    Check out the [Analysis Page](./2_Analysis) for
    our weekly market outlook on U.S. Gulf Coast Kerosene-Type Jetfuel.
    """
)

# -----------------------------------------------------------------------------
# Footer Section (footer.py)
# -----------------------------------------------------------------------------
