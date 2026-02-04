from pathlib import Path

import streamlit as st

# -----------------------------------------------------------------------------
# Data Configuration
# -----------------------------------------------------------------------------
# Manual entry for historical accuracy tracking
# Valid directions: "⬆️", "⬇️", "➡️", "❓"
REPORT_HISTORY = [
    {
        "week": 2,
        "predicted": "⬇️",
        "actual": "⬇️",
        "filename": "resources/reports/jetdash_week_2_report.pdf",
    },
    {
        "week": 1,
        "predicted": "⬇️",
        "actual": "⬆️",
        "filename": "resources/reports/jetdash_week_1_report.pdf",
    },
    # Add older weeks here...
]


def render_historical_report_section():
    """
    Renders a table of past reports with accuracy indicators
    and download links.
    """
    st.subheader("Historical Analysis Archive")
    st.caption("Review past performance and download archived PDF reports.")

    # -------------------------------------------------------------------------
    # Table Header
    # -------------------------------------------------------------------------
    # We use columns to simulate a table header
    h_col1, h_col2, h_col3, h_col4 = st.columns([1, 1, 1, 2])
    h_col1.markdown("**Week**")
    h_col2.markdown("**Predicted**")
    h_col3.markdown("**Actual**")
    h_col4.markdown("**Download**")

    st.divider()

    # -------------------------------------------------------------------------
    # Table Rows
    # -------------------------------------------------------------------------

    for report in REPORT_HISTORY:
        week = report["week"]
        pred = report["predicted"]
        act = report["actual"]
        fname = report["filename"]

        # Determine Color Logic: Green (success) if match, Red (error) if not
        is_correct = pred == act
        container_type = st.success if is_correct else st.error

        # Determine File Availability
        file_path = fname
        file_data = None
        is_disabled = True

        print(Path(file_path).exists())
        import os

        print(os.listdir())

        if Path(file_path).exists():
            print(f"Found historical report: {file_path}")
            with open(file_path, "rb") as f:
                file_data = f.read()
            is_disabled = False

        # Render Row inside the colored container
        with container_type(body=True):
            r_col1, r_col2, r_col3, r_col4 = st.columns(
                [1, 1, 1, 2], vertical_alignment="center"
            )

            with r_col1:
                st.markdown(f"**Week {week}**")

            with r_col2:
                st.markdown(f"{pred}")

            with r_col3:
                st.markdown(f"{act}")

            with r_col4:
                if not is_disabled:
                    st.download_button(
                        label="Download PDF",
                        data=file_data,
                        file_name=fname,
                        mime="application/pdf",
                        key=f"btn_hist_{week}",
                    )
                else:
                    st.button(
                        "Unavailable", disabled=True, key=f"btn_hist_{week}"
                    )


if __name__ == "__main__":
    render_historical_report_section()
