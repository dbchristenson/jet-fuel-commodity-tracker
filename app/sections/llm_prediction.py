import json
import time
from pathlib import Path

import streamlit as st

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def load_prediction():
    """Loads the cached prediction file."""
    # Assuming the data is in root/data and this script
    # is app/sections/llm_prediction.py
    data_path = (
        Path(__file__).parents[2] / "data" / "llm_prediction_snapshot.json"
    )

    try:
        with open(data_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def stream_text(text):
    """Generator to simulate typing effect."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)  # Adjust speed here


# -----------------------------------------------------------------------------
# Rendering
# -----------------------------------------------------------------------------


def render_llm_section():
    """Renders the Gemini Prediction Interface."""

    # 1. Load Data
    snapshot = load_prediction()

    # If no data exists, show a placeholder
    if not snapshot:
        st.warning(
            "⚠️ No prediction data found. "
            "Please run 'get_current_events.py' "
            "to generate an initial analysis."
        )
        return

    last_updated = snapshot.get("last_updated", "Unknown")
    prediction_text = snapshot.get("prediction", "")

    # 2. Header with timestamp
    st.caption(f"Last Analysis Run: {last_updated}")

    # 3. Chat Interface
    # Using the Google Gemini logo for the avatar
    gemini_avatar = (
        "https://www.gstatic.com/lamda/images"
        "/gemini_sparkle_v002_d4735304ff6292a690345.svg"
    )

    with st.chat_message("assistant", avatar=gemini_avatar):
        st.write("### Market Outlook")

        if "prediction_shown" not in st.session_state:
            st.session_state.prediction_shown = False

        if not st.session_state.prediction_shown:
            # The Typing Effect
            st.write_stream(stream_text(prediction_text))
            st.session_state.prediction_shown = True
        else:
            # Static display after first load
            st.markdown(prediction_text)

    # 4. Context Footer (Optional, adds credibility)
    with st.expander("View Analysis Context"):
        st.info(
            f"Analysis based on {snapshot.get('news_source_count', 0)}"
            " news sources and recent EIA quantitative data."
        )
