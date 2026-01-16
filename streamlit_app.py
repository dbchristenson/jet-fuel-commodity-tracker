import os
import random
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.analytics import data_granularity_and_aggregate_stats

# Roll for image
if "header_image" not in st.session_state:

    # This block only runs ONCE per user session (on page load/refresh)
    headers_dir = Path("resources") / "headers"
    available_files = os.listdir(headers_dir)

    if available_files:
        # random.choice is cleaner than randint with indices
        selected_file = random.choice(available_files)

        print("DO A BARREL ROLL: New image selected.")
        print(f"image_location: {selected_file}")

        # Save the result to session state
        st.session_state["header_image"] = headers_dir / selected_file
    else:
        st.session_state["header_image"] = None

# Retrieve the image from state (this happens on every rerun)
image_url = st.session_state["header_image"]

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Jet Fuel Commodity Tracker",
    page_icon=":earth_americas:",
)

# -----------------------------------------------------------------------------


def clean_df(df: pd.DataFrame, commodity_name: str):
    """
    Clean up the dataframe:
    1. Convert 'Date' to datetime.
    2. Rename the price column to a standard 'Price'.
    3. Add a metadata column for the 'Asset'.
    """
    df["Date"] = pd.to_datetime(df["Date"])

    # Rename the value column (index 1) to 'Price' so all dataframes match
    # standardized names are required for pd.concat to stack them correctly
    df.rename(columns={df.columns[1]: "Price"}, inplace=True)

    # Create the new column specifying the asset
    df["Asset"] = commodity_name

    return df


def join_dfs_on_date(dfs: list[pd.DataFrame]):
    """
    Stack multiple dataframes vertically.

    Since we standardized the columns to ['Date', 'Price', 'Asset'],
    we use concat instead of merge.
    """
    merged_df = pd.concat(dfs, axis=0, ignore_index=True)

    # Optional: Sort by date to keep things tidy
    merged_df = merged_df.sort_values(by=["Date", "Asset"])

    return merged_df


def transform_commodity_df(df: pd.DataFrame):
    """Transform the commodity dataframe."""

    # Split the 'Date' column into 'Year' and 'Month' columns
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    return df


@st.cache_data
def get_commodity_data():
    """
    Grab commodity data from Excel files.
    """
    data_dir = Path(__file__).parent / "data"

    # Check if directory exists to avoid errors if folder is missing
    if not data_dir.exists():
        st.error(f"Data directory not found at {data_dir}")
        return pd.DataFrame(), []

    data_children = os.listdir(data_dir)

    commodity_data = (
        []
    )  # Changed from dict to list, as we just need a list for concat
    assets = []

    for child in data_children:
        if child.endswith(".xlsx"):
            commodity_name = child.replace("commodity_", "").replace(
                "_prices.xlsx", ""
            )
            assets.append(commodity_name)

            file_path = data_dir / child
            # Added check for file existence/readability is good practice
            try:
                df = pd.read_excel(file_path, skiprows=2, sheet_name="Data 1")

                # Convert the 'Date' column and add 'Asset' column
                df = clean_df(df, commodity_name=commodity_name)

                commodity_data.append(df)
            except Exception as e:
                st.warning(f"Could not process {child}: {e}")

    if not commodity_data:
        return pd.DataFrame(), assets

    commodity_df = join_dfs_on_date(commodity_data)
    commodity_df = transform_commodity_df(commodity_df)

    return commodity_df, assets


commodity_df, assets = get_commodity_data()

# -----------------------------------------------------------------------------
# Streamlit App Layout
"""
# :airplane: Jet Fuel Commodity Dashboard
"""
if image_url:
    st.image(str(image_url), width="stretch")
"""
"""

col1a, col2a = st.columns(2)
# Year Selection
min_value = commodity_df["Year"].min()
max_value = commodity_df["Year"].max()

with col1a:
    from_year, to_year = st.slider(
        "Which years are you interested in?",
        min_value=min_value,
        max_value=max_value,
        value=[2020, max_value],
    )

# Asset Selection
if not len(assets):
    st.warning("Select at least one asset")

with col2a:
    selected_assets = st.multiselect(
        "Which assets would you like to view?",
        assets,
        default=assets[0],
        format_func=str.capitalize,
    )

# Filter the data
filtered_assets_df = commodity_df[
    (commodity_df["Asset"].isin(selected_assets))
    & (commodity_df["Year"] <= to_year)
    & (from_year <= commodity_df["Year"])
]

# Frequency and Aggregation
col1b, col2b = st.columns(2)

with col1b:
    freq_selection = st.radio(
        "Select Frequency:",
        options=["Daily", "Weekly", "Monthly"],
        horizontal=True,
    )

with col2b:
    agg_method = st.radio(
        "Aggregation Method:",
        options=["Average Price", "Close Price"],
        horizontal=True,
    )

df_plot = data_granularity_and_aggregate_stats(
    freq_selection, agg_method, filtered_assets_df
)

""
""

st.header("US Commodity Prices over Time", divider="gray")
title_text = f"{freq_selection} Commodity Prices ({agg_method})"

fig = px.line(df_plot, x="Date", y="Price", color="Asset", title=title_text)
fig.update_layout(legend_title_text="Commodity Name", hovermode="x unified")

st.plotly_chart(fig)

""
""

st.header("Jet Fuel Current Events and News", divider="gray")
