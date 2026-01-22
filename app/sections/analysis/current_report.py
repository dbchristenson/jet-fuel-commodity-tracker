from pathlib import Path

import streamlit as st

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
CURRENT_WEEK = 2  # Manually update this week number


def render_current_report_section():
    """
    Renders the download section for the current week's report.
    """
    st.header(f"Week {CURRENT_WEEK} Analysis Report", divider="gray")

    # Construct the file path relative to the project root
    # Assumption: Structure is root/app/sections/current_report.py
    # So we go up two levels to root, then into resources/reports
    project_root = Path(__file__).parents[2]
    filename = f"jetdash_week_{CURRENT_WEEK}_report.pdf"
    file_path = project_root / "resources" / "reports" / filename

    # Check if report exists
    if file_path.exists():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.info(
                f"**The Week {CURRENT_WEEK} analysis is ready.**\n\n"
                "This report includes a dive into recent refinery outages "
                "in PADD 3 and their impact on jet fuel crack spreads."
            )

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
