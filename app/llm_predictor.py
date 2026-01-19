import os

import streamlit as st
from google import genai

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

if not GEMINI_API_KEY:
    # fallback to environment variable
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def build_llm_contents():
    """
    Take in all available intelligence to build the contents
    of the LLM prompt.
    """
    return


def generate_prediction(prompt: str):
    """
    Generates a prediction for jet fuel prices based on several
    variables like joint commodity prices, geopolitical events,
    and historical trends. Pretty much guessing though tbh.
    """
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    return response.text
