import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

current_date = datetime.datetime.now().strftime("%Y-%m-%d")
past_30_days = (
    datetime.datetime.now() - datetime.timedelta(days=30)
).strftime("%Y-%m-%d")

LATEST_JET_FUEL_NEWS_URL = "https://www.argusmedia.com/en/news-and-insights/latest-market-news?filters=%7B%22language%22%3A%22%27en-gb%27%22%2C%22commodity%22%3A%22%27Biofuels%27%2C%27Base+Oil%27%2C%27Oil+Products%27%22%2C%22market%22%3A%22%27Jet+Fuel-Kerosine%27%22%7D&page=1&filter_language=en-gb&filter_commodity=oil+products%3Abiofuels%2Cbase+oil%2Coil+products&filter_market=jet+fuels%3Ajet+fuel-kerosine"

def fetch_latest_jet_fuel_news():
