import json

import streamlit as st

from app.extract_article import extract_article_info
from app.sections.analysis.report_renderer import (
    load_all_reports,
    load_report,
    save_report,
)

st.set_page_config(page_title="Admin", page_icon="\U0001f512")

# Load current week
CURRENT_WEEK_JSON_DATA = "data/current_week.json"
CURRENT_WEEK = 1

with open(CURRENT_WEEK_JSON_DATA, "r") as json_file:
    data = json.load(json_file)
    CURRENT_WEEK = data.get("current_week", CURRENT_WEEK)

# ---------------------------------------------------------------------------
# Authentication Gate
# ---------------------------------------------------------------------------
st.title("\U0001f512 Admin")

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    password = st.text_input("Enter admin password:", type="password")
    if st.button("Unlock"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

# ---------------------------------------------------------------------------
# Authenticated content below
# ---------------------------------------------------------------------------

# Initialize session state for articles
if "admin_articles" not in st.session_state:
    existing = load_report(CURRENT_WEEK)
    if existing:
        st.session_state.admin_articles = existing.get("selected_articles", [])
    else:
        st.session_state.admin_articles = []

if "extracted_article" not in st.session_state:
    st.session_state.extracted_article = None

# ---------------------------------------------------------------------------
# Section A: Create/Edit Current Week Report
# ---------------------------------------------------------------------------
st.header(f"Create/Edit Week {CURRENT_WEEK} Report", divider="gray")

existing_report = load_report(CURRENT_WEEK)

DIRECTION_OPTIONS = ["\u2b06\ufe0f Up", "\u2b07\ufe0f Down", "\u27a1\ufe0f Flat", "\u2753 Uncertain"]
DIRECTION_MAP = {
    "\u2b06\ufe0f Up": "\u2b06\ufe0f",
    "\u2b07\ufe0f Down": "\u2b07\ufe0f",
    "\u27a1\ufe0f Flat": "\u27a1\ufe0f",
    "\u2753 Uncertain": "\u2753",
}

# Pre-fill defaults from existing report
default_date_range = ""
default_predicted_idx = 0
default_commentary = ""

if existing_report:
    default_date_range = existing_report.get("date_range", "")
    pred = existing_report.get("predicted", "")
    # Find the matching index in DIRECTION_OPTIONS
    for i, opt in enumerate(DIRECTION_OPTIONS):
        if DIRECTION_MAP[opt] == pred:
            default_predicted_idx = i
            break
    default_commentary = existing_report.get("commentary", "") or ""

with st.form("report_form"):
    date_range = st.text_input("Date Range", value=default_date_range,
                               placeholder="e.g. Feb 10 - Feb 14, 2026")
    predicted = st.selectbox("Prediction", DIRECTION_OPTIONS,
                             index=default_predicted_idx)
    commentary = st.text_area("Analyst Commentary (Markdown)",
                              value=default_commentary, height=200)

    submitted = st.form_submit_button("\U0001f4be Save Report", type="primary")

    if submitted:
        report = {
            "week": CURRENT_WEEK,
            "date_range": date_range,
            "predicted": DIRECTION_MAP[predicted],
            "actual": existing_report.get("actual") if existing_report else None,
            "commentary": commentary if commentary.strip() else None,
            "selected_articles": st.session_state.admin_articles,
        }
        save_report(report)
        st.success(f"Week {CURRENT_WEEK} report saved!")

# ---------------------------------------------------------------------------
# Article Adder (outside the form for dynamic interaction)
# ---------------------------------------------------------------------------
st.subheader("Add Articles")

url_input = st.text_input("Paste article URL:", key="article_url_input")

if st.button("Extract with Gemini"):
    if url_input.strip():
        with st.spinner("Extracting article info..."):
            result = extract_article_info(url_input.strip())
        if result:
            st.session_state.extracted_article = result
            st.session_state.extracted_article["link"] = url_input.strip()
        else:
            st.error("Failed to extract article information.")
    else:
        st.warning("Please paste a URL first.")

# Show extracted article for review
if st.session_state.extracted_article:
    article = st.session_state.extracted_article
    st.markdown(f"**Extracted:** {article.get('title', 'No title')}")
    st.markdown(f"**Summary:** {article.get('summary', 'No summary')}")
    st.markdown(f"**Date:** {article.get('date', 'Unknown')}")

    analyst_note = st.text_area(
        "Your analysis (optional — takes display precedence over summary):",
        key="analyst_note_input",
    )

    if st.button("Add to Report"):
        new_article = {
            "title": article.get("title", ""),
            "summary": article.get("summary", ""),
            "analyst_note": analyst_note.strip() if analyst_note.strip() else None,
            "date": article.get("date", ""),
            "link": article.get("link", ""),
        }
        st.session_state.admin_articles.append(new_article)
        st.session_state.extracted_article = None
        st.rerun()

# Show current article list
if st.session_state.admin_articles:
    st.markdown(f"**Current articles: ({len(st.session_state.admin_articles)})**")
    for i, art in enumerate(st.session_state.admin_articles):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"{i + 1}. {art.get('title', 'Untitled')}")
        with col2:
            if st.button("Remove", key=f"remove_article_{i}"):
                st.session_state.admin_articles.pop(i)
                st.rerun()

# ---------------------------------------------------------------------------
# Section B: Update Historical Actuals
# ---------------------------------------------------------------------------
st.header("Update Historical Actuals", divider="gray")

all_reports = load_all_reports()
pending_reports = [
    r for r in all_reports
    if r.get("actual") is None and r.get("week") != CURRENT_WEEK
]

if not pending_reports:
    st.info("No historical weeks with pending actuals.")
else:
    for report in pending_reports:
        week = report["week"]
        pred = report.get("predicted", "❓")

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.markdown(f"**Week {week}**: predicted {pred}")

        with col2:
            actual = st.selectbox(
                "Actual",
                DIRECTION_OPTIONS,
                key=f"actual_select_{week}",
                label_visibility="collapsed",
            )

        with col3:
            if st.button("Save", key=f"save_actual_{week}"):
                report["actual"] = DIRECTION_MAP[actual]
                save_report(report)
                st.success(f"Week {week} actual updated!")
                st.rerun()
