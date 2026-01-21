import os

import requests
import streamlit as st

EIA_REFINERY_DATA_URL = "https://api.eia.gov/v2/petroleum/pnp/refp2/data/?frequency=monthly&data[0]=value&facets[series][]=MDIRX_NUS_1&facets[series][]=MDIRX_NUS_2&facets[series][]=MDIRX_R30_1&facets[series][]=MDIRX_R30_2&facets[series][]=MG4RX_R30_1&facets[series][]=MG4RX_R30_2&facets[series][]=MG6RX_NUS_1&facets[series][]=MG6RX_NUS_2&facets[series][]=M_EPJKC_YPY_NUS_MBBL&facets[series][]=M_EPJKC_YPY_NUS_MBBLD&facets[series][]=M_EPJKC_YPY_R30_MBBL&facets[series][]=M_EPJKC_YPY_R30_MBBLD&start=1993-01&end=2025-10&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"  # noqa E501
EIA_SPOT_PRICE_DATA_URL = "https://api.eia.gov/v2/petroleum/pri/spt/data/?frequency=daily&data[0]=value&facets[series][]=EER_EPD2DXL0_PF4_RGC_DPG&facets[series][]=EER_EPJK_PF4_RGC_DPG&facets[series][]=EER_EPMRU_PF4_RGC_DPG&start=1986-01-03&end=2026-01-09&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"  # noqa E501
EIA_API_KEY = st.secrets["EIA_API_KEY"]

if not EIA_API_KEY:
    # environment variable fallback
    EIA_API_KEY = os.getenv("EIA_API_KEY")


REFINERY_REQUEST = EIA_REFINERY_DATA_URL + f"&api_key={EIA_API_KEY}"
SPOT_PRICE_REQUEST = EIA_SPOT_PRICE_DATA_URL + f"&api_key={EIA_API_KEY}"


def fetch_refinery_data():
    """Fetch refinery utilization data from EIA API."""
    try:
        response = requests.get(REFINERY_REQUEST)
        response.raise_for_status()
        data = response.json()

        records = data.get("response", {}).get("data", [])
        if not records:
            print("No data found in EIA response.")
            return []

        print(f"Fetched {len(records)} records from EIA API.")
        return records

    except requests.RequestException as e:
        print(f"Error fetching data from EIA API: {e}")
        return []


def fetch_spot_price_data():
    """Fetch spot price data from EIA API."""
    try:
        response = requests.get(SPOT_PRICE_REQUEST)
        response.raise_for_status()
        data = response.json()

        records = data.get("response", {}).get("data", [])
        if not records:
            print("No data found in EIA response.")
            return []

        print(f"Fetched {len(records)} records from EIA API.")
        return records

    except requests.RequestException as e:
        print(f"Error fetching data from EIA API: {e}")
        return []


def save_data_to_file(data, filename):
    """Save fetched data to a JSON file."""
    import json

    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")


if __name__ == "__main__":
    refinery_data = fetch_refinery_data()
    save_data_to_file(refinery_data, "data/refinery_utilization.json")

    spot_price_data = fetch_spot_price_data()
    save_data_to_file(spot_price_data, "data/spot_prices.json")
