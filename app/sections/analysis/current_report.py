import json

import streamlit as st

from app.sections.analysis.report_renderer import load_report, render_report_body

CURRENT_WEEK_JSON_DATA = "data/current_week.json"
CURRENT_WEEK = 1

with open(CURRENT_WEEK_JSON_DATA, "r") as json_file:
    data = json.load(json_file)
    CURRENT_WEEK = data.get("current_week", CURRENT_WEEK)


def render_current_report_section():
    """Renders the current week's analysis report natively in Streamlit."""
    st.header(f"Week {CURRENT_WEEK} Analysis Report", divider="gray")

    report = load_report(CURRENT_WEEK)

    if report:
        render_report_body(report)
    else:
        st.warning(
            f"\u26a0\ufe0f **Report Not Found**: The analysis for Week {CURRENT_WEEK} "
            "has not been published yet. Please check back later."
        )


if __name__ == "__main__":
    render_current_report_section()
