import json
import os
import re

import google.generativeai as genai
import requests
import streamlit as st
from bs4 import BeautifulSoup

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")


def extract_article_info(url: str) -> dict | None:
    """
    Fetches a URL, extracts the page text, and uses Gemini to extract
    the article title, a 3-sentence summary, and the publication date.

    Returns a dict with keys: title, summary, date.
    Returns None on failure.
    """
    try:
        response = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to fetch URL: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # Remove script/style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    page_text = soup.get_text(separator="\n", strip=True)

    # Truncate to avoid exceeding token limits
    page_text = page_text[:10000]

    if not page_text.strip():
        st.error("Could not extract text from the page.")
        return None

    if not GOOGLE_API_KEY:
        st.error("GEMINI_API_KEY not configured.")
        return None

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-3-flash-preview")

    prompt = f"""Extract ONLY the following from this article:
1. The article title
2. A summary in exactly 3 sentences or less
3. The publication date

Return as JSON: {{"title": "...", "summary": "...", "date": "YYYY-MM-DD"}}
Do not add any commentary or analysis. Extract only what is in the article.

Article text:
{page_text}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown code fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        result = json.loads(text)
        return result
    except (json.JSONDecodeError, Exception) as e:
        st.error(f"Gemini extraction failed: {e}")
        return None
