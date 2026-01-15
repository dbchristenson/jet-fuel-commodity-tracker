import os
from pathlib import Path

import pandas as pd
import streamlit as st

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

    return commodity_df, assets


commodity_df, assets = get_commodity_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
"""
# :earth_americas: Jet Fuel Commodity Dashboard
"""

# Add some spacing
"""
"""

min_value = commodity_df["Year"].min()
max_value = commodity_df["Year"].max()

from_year, to_year = st.slider(
    "Which years are you interested in?",
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value],
)

if not len(assets):
    st.warning("Select at least one asset")

selected_assets = st.multiselect(
    "Which assets would you like to view?", assets, default=assets[0]
)

""
""
""

# Filter the data
filtered_assets_df = commodity_df[
    (commodity_df["Asset"].isin(selected_assets))
    & (commodity_df["Year"] <= to_year)
    & (from_year <= commodity_df["Year"])
]

st.header("Commodity Prices over Time", divider="gray")

""
""

first_year = commodity_df[commodity_df["Year"] == from_year]
last_year = commodity_df[commodity_df["Year"] == to_year]

st.header(f"GDP in {to_year}", divider="gray")

""

cols = st.columns(4)

for i, asset in enumerate(assets):
    st.line_chart(
        commodity_df,
        x="Date",
        y=asset,
    )
