import json
from pathlib import Path

import streamlit as st

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
CURRENT_WEEK_JSON_DATA = "data/current_week.json"
CURRENT_WEEK = 1

with open(CURRENT_WEEK_JSON_DATA, "r") as json_file:
    data = json.load(json_file)
    CURRENT_WEEK = data.get("current_week", CURRENT_WEEK)


def render_current_report_section():
    """
    Renders the download section for the current week's report.
    """
    st.header(f"Week {CURRENT_WEEK} Analysis Report", divider="gray")
    filename = f"jetdash_week_{CURRENT_WEEK}_report.pdf"
    file_path = "resources/reports/" + filename

    # Check if report exists
    if Path(file_path).exists():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.info(f"**The Week {CURRENT_WEEK} analysis is ready.**")

        with col2:
            # Centering the large button
            st.write("")
            st.write("")
            with open(file_path, "rb") as pdf_file:
                st.download_button(
                    label=f"📄 Download Week {CURRENT_WEEK} Report",
                    data=pdf_file,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )
    else:
        # Warning Card
        st.warning(
            f"⚠️ **Report Not Found**: The analysis for Week {CURRENT_WEEK} "
            "has not been published yet. Please check back later."
        )


if __name__ == "__main__":
    render_current_report_section()
