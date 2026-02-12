import datetime as dt
import json
import os

import requests
import streamlit as st

# Setup EIA API Key
EIA_API_KEY = os.getenv("EIA_API_KEY") or st.secrets.get("EIA_API_KEY")

if not EIA_API_KEY:
    raise ValueError(
        "EIA_API_KEY not found in Environment or Streamlit Secrets"
    )


def fetch_refinery_data(start_date=None, end_date=None):
    """
    Fetch monthly refinery utilization data from EIA API.
    start_date and end_date should be in 'YYYY-MM' format.
    """
    # Defaults handled in main, but safe fallbacks here
    if not start_date:
        start_date = "1993-01"
    if not end_date:
        end_date = dt.date.today().strftime("%Y-%m")

    EIA_REFINERY_DATA_URL = f"https://api.eia.gov/v2/petroleum/pnp/refp2/data/?frequency=monthly&data[0]=value&facets[series][]=MDIRX_NUS_1&facets[series][]=MDIRX_NUS_2&facets[series][]=MDIRX_R30_1&facets[series][]=MDIRX_R30_2&facets[series][]=MG4RX_R30_1&facets[series][]=MG4RX_R30_2&facets[series][]=MG6RX_NUS_1&facets[series][]=MG6RX_NUS_2&facets[series][]=M_EPJKC_YPY_NUS_MBBL&facets[series][]=M_EPJKC_YPY_NUS_MBBLD&facets[series][]=M_EPJKC_YPY_R30_MBBL&facets[series][]=M_EPJKC_YPY_R30_MBBLD&start={start_date}&end={end_date}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"  # noqa E501
    REFINERY_REQUEST = EIA_REFINERY_DATA_URL + f"&api_key={EIA_API_KEY}"

    try:
        response = requests.get(REFINERY_REQUEST)
        response.raise_for_status()
        data = response.json()

        records = data.get("response", {}).get("data", [])
        if not records:
            print(
                f"No new refinery data found for {start_date} to {end_date}."
            )
            return []

        print(f"Fetched {len(records)} refinery records from EIA API.")
        return records

    except requests.RequestException as e:
        print(f"Error fetching refinery data: {e}")
        return []


def fetch_spot_price_data(start_date=None, end_date=None):
    """
    Fetch daily spot price data from EIA API.
    start_date and end_date should be in 'YYYY-MM-DD' format.
    """
    if not start_date:
        start_date = "1986-01-03"
    if not end_date:
        end_date = dt.date.today().strftime("%Y-%m-%d")

    EIA_SPOT_PRICE_DATA_URL = f"https://api.eia.gov/v2/petroleum/pri/spt/data/?frequency=daily&data[0]=value&facets[series][]=EER_EPD2DXL0_PF4_RGC_DPG&facets[series][]=EER_EPJK_PF4_RGC_DPG&facets[series][]=EER_EPMRU_PF4_RGC_DPG&start={start_date}&end={end_date}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"  # noqa E501
    SPOT_PRICE_REQUEST = EIA_SPOT_PRICE_DATA_URL + f"&api_key={EIA_API_KEY}"

    try:
        response = requests.get(SPOT_PRICE_REQUEST)
        response.raise_for_status()
        data = response.json()

        records = data.get("response", {}).get("data", [])
        if not records:
            print(
                f"No new spot price data found for {start_date} to {end_date}."
            )
            return []

        print(f"Fetched {len(records)} spot price records from EIA API.")
        return records

    except requests.RequestException as e:
        print(f"Error fetching spot price data: {e}")
        return []


def load_data_from_file(filename):
    """Load existing data from JSON file if it exists."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading {filename}: {e}")
        return []


def save_merged_data(new_records, filename):
    """
    Merges new records with existing file data and saves.
    Deduplicates based on 'period' and 'series' to prevent overlaps.
    """
    existing_data = load_data_from_file(filename)

    # Create a dictionary keyed by unique attributes to handle deduplication
    # EIA data usually has a 'series' or 'series-description' and a 'period'
    # We use these to update existing records with new values
    data_map = {}

    # 1. Load old data into map
    for record in existing_data:
        # Create a unique key. Fallback to just period if series is missing,
        # but EIA v2 usually provides series IDs.
        key = (record.get("period"), record.get("series"))
        data_map[key] = record

    # 2. Update with new data
    for record in new_records:
        key = (record.get("period"), record.get("series"))
        data_map[key] = record

    # 3. Convert back to list and sort
    merged_list = list(data_map.values())

    # Sort by period descending (standard EIA format)
    merged_list.sort(key=lambda x: x.get("period", ""), reverse=True)

    try:
        with open(filename, "w") as f:
            json.dump(merged_list, f, indent=4)
        print(f"Successfully saved {len(merged_list)} records to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")


def get_latest_period(data):
    """Helper to find the max date in a list of records."""
    if not data:
        return None
    return max(record["period"] for record in data)


if __name__ == "__main__":
    today = dt.date.today()

    # ---------------------------------------------------------
    # 1. Update Refinery Data (Monthly)
    # ---------------------------------------------------------
    refinery_file = "data/refinery_utilization.json"
    existing_refinery = load_data_from_file(refinery_file)

    # Determine start date
    latest_refinery_date = get_latest_period(existing_refinery)
    if latest_refinery_date:
        start_date_ref = latest_refinery_date
    else:
        start_date_ref = "1993-01"

    # Determine end date (Current Month)
    end_date_ref = today.strftime("%Y-%m")

    print(f"Updating Refinery Data: {start_date_ref} -> {end_date_ref}")
    new_refinery_data = fetch_refinery_data(start_date_ref, end_date_ref)

    if new_refinery_data:
        save_merged_data(new_refinery_data, refinery_file)
    else:
        print("Refinery data is already up to date.")

    # ---------------------------------------------------------
    # 2. Update Spot Price Data (Daily)
    # ---------------------------------------------------------
    spot_file = "data/spot_prices.json"
    existing_spot = load_data_from_file(spot_file)

    # Determine start date
    latest_spot_date = get_latest_period(existing_spot)
    if latest_spot_date:
        start_date_spot = latest_spot_date
    else:
        start_date_spot = "1986-01-03"

    # Determine end date (Today)
    end_date_spot = today.strftime("%Y-%m-%d")

    print(f"Updating Spot Prices: {start_date_spot} -> {end_date_spot}")
    new_spot_data = fetch_spot_price_data(start_date_spot, end_date_spot)

    if new_spot_data:
        save_merged_data(new_spot_data, spot_file)
    else:
        print("Spot price data is already up to date.")
