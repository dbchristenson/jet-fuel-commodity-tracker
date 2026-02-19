import json

import streamlit as st

from app.sections.analysis.report_renderer import (
    load_all_reports,
    render_report_body,
)

CURRENT_WEEK_JSON_DATA = "data/current_week.json"
CURRENT_WEEK = 1

with open(CURRENT_WEEK_JSON_DATA, "r") as json_file:
    data = json.load(json_file)
    CURRENT_WEEK = data.get("current_week", CURRENT_WEEK)


def render_historical_report_section():
    """
    Renders an accuracy table for past reports with expandable
    native report views.
    """
    st.subheader("Historical Analysis Archive")
    st.caption("Review past performance and archived analysis reports.")

    all_reports = load_all_reports()
    # Filter out the current week
    historical = [r for r in all_reports if r.get("week") != CURRENT_WEEK]

    if not historical:
        st.info("No historical reports available yet.")
        return

    # Table Header
    h_col1, h_col2, h_col3 = st.columns([1, 1, 1])
    h_col1.markdown("**Week**")
    h_col2.markdown("**Predicted**")
    h_col3.markdown("**Actual**")

    st.divider()

    # Table Rows
    for report in historical:
        week = report.get("week")
        pred = report.get("predicted", "❓")
        actual = report.get("actual")

        # Color logic: green if correct, red if wrong, info if pending
        if actual is None:
            container_type = st.info
        elif pred == actual:
            container_type = st.success
        else:
            container_type = st.error

        with container_type(body=True):
            r_col1, r_col2, r_col3 = st.columns(
                [1, 1, 1], vertical_alignment="center"
            )

            with r_col1:
                st.markdown(f"**Week {week}**")

            with r_col2:
                st.markdown(f"{pred}")

            with r_col3:
                st.markdown(f"{actual if actual else 'Pending'}")

        # Expandable full report
        with st.expander(f"View Week {week} Report"):
            render_report_body(report)


if __name__ == "__main__":
    render_historical_report_section()
