import json
import os
from datetime import datetime, timedelta

import google.generativeai as genai
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]

DATA_DIR = "data"
PREDICTION_FILE = os.path.join(DATA_DIR, "llm_prediction_snapshot.json")

# -----------------------------------------------------------------------------
# 1. Fetch News Logic
# -----------------------------------------------------------------------------


def fetch_market_news():
    """
    Fetches the last 28 days of news relevant to Jet Fuel and Distillates.
    NewsAPI Free Tier limits:
    - 100 requests/day
    - Data up to 1 month old
    """
    print("Fetching news from NewsAPI...")

    # Calculate date range (NewsAPI free tier limit is ~1 month)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Query optimized for energy market keywords
    # OR logic puts breadth, AND logic ensures relevance.
    query = (
        "tariff OR trump OR opec or sanctions OR oil OR refinery OR distillate"
        "OR jet fuel OR diesel OR war OR conflict OR gulf coast OR hurricane "
        "OR recession OR inflation"
    )

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": start_date.strftime("%Y-%m-%d"),
        "sortBy": "relevancy",
        "language": "en",
        "apiKey": NEWS_API_KEY,
        "pageSize": 20,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])

        # Digest: Keep only what the LLM needs
        digest = []
        for art in articles:
            digest.append(
                {
                    "date": art.get("publishedAt", "")[:10],
                    "title": art.get("title", ""),
                    "source": art.get("source", {}).get("name", ""),
                    "description": art.get("description", ""),
                }
            )

        print(f"Fetched {len(digest)} articles.")
        return digest

    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


# -----------------------------------------------------------------------------
# 2. Load Local Market Data
# -----------------------------------------------------------------------------


def load_local_data(filename):
    """Loads the last 10 records of data to give the LLM context."""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            # Assuming data is sorted desc, take top 10
            return data[:10] if data else []
    except Exception:
        return []


# -----------------------------------------------------------------------------
# 3. Generate Prediction (The "Bundle")
# -----------------------------------------------------------------------------


def generate_prediction(news_data, price_data, refinery_data):
    """
    Sends aggregated context to Gemini Flash for a market prediction.
    """
    print("Generating prediction with Gemini...")

    if not GOOGLE_API_KEY:
        print("Error: GEMINI_API_KEY not found.")
        return None

    genai.configure(api_key=GOOGLE_API_KEY)

    # Use Flash for speed and high context window (1M tokens)
    model = genai.GenerativeModel("gemini-3-flash-preview")

    # Construct the Prompt
    prompt = f"""
    You are an expert energy market analyst specializing
    in US Distillates (Jet Fuel, Diesel).

    ### Task
    Analyze the provided recent news headlines and quantitative
    market data to produce a short market outlook.

    ### Context Data

    1. **Recent Market News (Last 30 Days):**
    {json.dumps(news_data, indent=2)}

    2. **Recent Spot Prices (Latest Records):**
    {json.dumps(price_data, indent=2)}

    3. **Recent Refinery Utilization (Latest Records):**
    {json.dumps(refinery_data, indent=2)}

    ### Output Requirements
    - **Tone:** Professional, objective, data-driven.
    - **Structure:**
        - **The Bottom Line:** A single sentence summary of
          the outlook (Bullish/Bearish/Neutral). However, you
          must make a prediction for up or down next week.
        - **Key Drivers:** Bullet points citing specific news or price
          movements from the data.
        - **Risk Factors:** What could go wrong?
    - **Constraint:** Do not mention you are an AI. Write as a market report.
      Keep it under 250 words.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return "Prediction unavailable due to API error."


# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # 1. Gather Data
    news_digest = fetch_market_news()
    spot_prices = load_local_data("spot_prices.json")
    refinery_data = load_local_data("refinery_utilization.json")

    # 2. Generate Prediction
    prediction_text = generate_prediction(
        news_digest, spot_prices, refinery_data
    )

    if prediction_text:
        # 3. Save to File
        output_payload = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prediction": prediction_text,
            "news_source_count": len(news_digest),
        }

        with open(PREDICTION_FILE, "w") as f:
            json.dump(output_payload, f, indent=4)

        print(f"Success! Prediction saved to {PREDICTION_FILE}")
    else:
        print("Failed to generate prediction.")
