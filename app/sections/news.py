import json

import streamlit as st

# -----------------------------------------------------------------------------
# Data Loading & Processing
# -----------------------------------------------------------------------------


def load_data(filename="data/argus_news_cache.json") -> list:
    """Returns json news data from cached file."""
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error(f"News data file not found: {filename}")
        return []


def get_article_details(article) -> tuple[str, str, str, str]:
    """Extract details and ensure URL is valid for external navigation."""
    display_card = article.get("display_card", {})
    title = display_card.get("title", "No Title")
    summary = display_card.get("summary", "No Summary")
    date = display_card.get("date", "")
    link = display_card.get("link", {})

    return title, summary, date, link


# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


def scroll_left():
    if st.session_state.news_scroll_index > 0:
        st.session_state.news_scroll_index -= 1


def scroll_right(max_index):
    if st.session_state.news_scroll_index < max_index:
        st.session_state.news_scroll_index += 1


# -----------------------------------------------------------------------------
# Rendering Logic
# -----------------------------------------------------------------------------


def render_news_card(article, index):
    """
    Renders a single article card.

    Args:
        article (dict): The article data.
        index (int): The unique index of this article in the full list.
                     Used to generate unique keys.
    """
    title, summary, date, url = get_article_details(article)

    # height=300 enables the internal scrolling you like.
    with st.container(height=300, border=True):
        st.markdown(f"**{title}**")
        st.caption(f"📅 {date}")
        st.markdown(summary)

        st.write("")  # Spacer

        if url:
            st.link_button("Read Source", url)
        else:
            st.button(
                "No Source Available", disabled=True, key=f"no_src_{index}"
            )


def render_news_section():
    data = load_data()

    if not data:
        st.info("No news articles available.")
        return

    # Initialize Session State
    if "news_scroll_index" not in st.session_state:
        st.session_state.news_scroll_index = 0

    # Constants
    CARDS_TO_SHOW = 3
    total_articles = len(data)
    max_start_index = max(0, total_articles - CARDS_TO_SHOW)

    # -------------------------------------------------------------------------
    # Layout: 3 News Cards
    # -------------------------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    current_idx = st.session_state.news_scroll_index
    visible_articles = data[current_idx : current_idx + CARDS_TO_SHOW]

    # We pass (current_idx + N) to the render function.
    # This ensures that even if two articles have the same title,
    # the unique index from the main list keeps their keys distinct.

    with col1:
        if len(visible_articles) > 0:
            render_news_card(visible_articles[0], current_idx + 0)

    with col2:
        if len(visible_articles) > 1:
            render_news_card(visible_articles[1], current_idx + 1)

    with col3:
        if len(visible_articles) > 2:
            render_news_card(visible_articles[2], current_idx + 2)

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------
    st.write("")

    nav_c1, nav_c2 = st.columns(2)

    with nav_c1:
        st.button(
            "⬅️ Previous",
            key="news_prev",
            on_click=scroll_left,
            disabled=(st.session_state.news_scroll_index == 0),
            use_container_width=True,
        )

    with nav_c2:
        st.button(
            "Next ➡️",
            key="news_next",
            on_click=scroll_right,
            args=(max_start_index,),
            disabled=(st.session_state.news_scroll_index >= max_start_index),
            use_container_width=True,
        )


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_news_section()
