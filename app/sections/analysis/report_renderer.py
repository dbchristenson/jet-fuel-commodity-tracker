import json
import glob as glob_module
from pathlib import Path

import streamlit as st

REPORTS_DIR = Path(__file__).parents[3] / "data" / "reports"
JOHN_AVATAR = "resources/avatars/john.png"


def load_report(week: int) -> dict | None:
    """Loads a single week's report JSON from data/reports/."""
    report_path = REPORTS_DIR / f"week_{week}_report.json"
    if not report_path.exists():
        return None
    try:
        with open(report_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def load_all_reports() -> list[dict]:
    """Scans directory for all week_*_report.json, sorted by week descending."""
    pattern = str(REPORTS_DIR / "week_*_report.json")
    files = glob_module.glob(pattern)
    reports = []
    for filepath in files:
        try:
            with open(filepath, "r") as f:
                report = json.load(f)
                reports.append(report)
        except (json.JSONDecodeError, IOError):
            continue
    reports.sort(key=lambda r: r.get("week", 0), reverse=True)
    return reports


def save_report(report: dict):
    """Writes a report dict to data/reports/week_{N}_report.json."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    week = report["week"]
    report_path = REPORTS_DIR / f"week_{week}_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)


def _render_direction_badge(report: dict):
    """Renders the predicted vs actual direction badge."""
    predicted = report.get("predicted", "❓")
    actual = report.get("actual")

    if actual is None:
        st.info(f"**Predicted:** {predicted}  |  **Actual:** Pending")
    elif predicted == actual:
        st.success(f"**Predicted:** {predicted}  |  **Actual:** {actual}")
    else:
        st.error(f"**Predicted:** {predicted}  |  **Actual:** {actual}")


def _render_commentary(report: dict):
    """Renders the analyst commentary using the chat_message pattern."""
    commentary = report.get("commentary")
    if not commentary:
        return

    with st.chat_message("assistant", avatar=JOHN_AVATAR):
        st.write("### Analyst Commentary")
        st.markdown(commentary)


def _render_articles(report: dict):
    """Renders selected articles in a 3-column card grid."""
    articles = report.get("selected_articles", [])
    if not articles:
        return

    st.markdown("**Key Articles**")

    # Render in rows of 3
    for i in range(0, len(articles), 3):
        row_articles = articles[i : i + 3]
        cols = st.columns(3)
        for j, article in enumerate(row_articles):
            with cols[j]:
                with st.container(height=300, border=True):
                    st.markdown(f"**{article.get('title', 'Untitled')}**")
                    date = article.get("date", "")
                    if date:
                        st.caption(f"\U0001f4c5 {date}")

                    # analyst_note takes precedence over summary
                    note = article.get("analyst_note")
                    summary = article.get("summary", "")
                    st.markdown(note if note else summary)

                    link = article.get("link")
                    if link:
                        st.link_button("Read Source", link)


def render_report_body(report: dict):
    """Renders the full native report."""
    _render_direction_badge(report)
    _render_commentary(report)
    _render_articles(report)
