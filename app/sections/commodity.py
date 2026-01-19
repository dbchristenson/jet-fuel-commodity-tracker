import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.analytics import data_granularity_and_aggregate_stats

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def clean_df(df: pd.DataFrame, commodity_name: str):
    """
    Clean up the dataframe:
    1. Convert 'Date' to datetime.
    2. Rename the price column to a standard 'Price'.
    3. Add a metadata column for the 'Asset'.
    """
    df["Date"] = pd.to_datetime(df["Date"])
    # Rename the value column (index 1) to 'Price'
    df.rename(columns={df.columns[1]: "Price"}, inplace=True)
    df["Asset"] = commodity_name
    return df


def join_dfs_on_date(dfs: list[pd.DataFrame]):
    """Stack multiple dataframes vertically."""
    merged_df = pd.concat(dfs, axis=0, ignore_index=True)
    merged_df = merged_df.sort_values(by=["Date", "Asset"])
    return merged_df


def transform_commodity_df(df: pd.DataFrame):
    """Add Year and Month columns."""
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    return df


@st.cache_data
def get_commodity_data():
    """Grab commodity data from Excel files."""
    # Adjusted path: Assuming structure is root/app/sections/commodity.py
    # and data is at root/data
    data_dir = Path(__file__).parents[2] / "data"

    if not data_dir.exists():
        st.error(f"Data directory not found at {data_dir}")
        return pd.DataFrame(), []

    data_children = os.listdir(data_dir)
    commodity_data = []
    assets = []

    for child in data_children:
        if child.endswith(".xlsx"):
            commodity_name = child.replace("commodity_", "").replace(
                "_prices.xlsx", ""
            )
            assets.append(commodity_name)
            file_path = data_dir / child

            try:
                df = pd.read_excel(file_path, skiprows=2, sheet_name="Data 1")
                df = clean_df(df, commodity_name=commodity_name)
                commodity_data.append(df)
            except Exception as e:
                st.warning(f"Could not process {child}: {e}")

    if not commodity_data:
        return pd.DataFrame(), assets

    commodity_df = join_dfs_on_date(commodity_data)
    commodity_df = transform_commodity_df(commodity_df)

    return commodity_df, assets


# -----------------------------------------------------------------------------
# Main Section Render
# -----------------------------------------------------------------------------


def render_commodity_section():
    """Renders the Commodity Price Visualization Section."""

    # Load Data
    commodity_df, assets = get_commodity_data()

    if commodity_df.empty:
        st.warning("No commodity data available to display.")
        return

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
    if not assets:
        st.warning("Select at least one asset")

    with col2a:
        selected_assets = st.multiselect(
            "Which assets would you like to view?",
            assets,
            default=assets[0] if assets else None,
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

    # Process stats for plotting
    df_plot = data_granularity_and_aggregate_stats(
        freq_selection, agg_method, filtered_assets_df
    )

    st.write("")
    st.write("")

    st.header("US Commodity Prices over Time", divider="gray")
    title_text = f"{freq_selection} Commodity Prices ({agg_method})"

    fig = px.line(
        df_plot, x="Date", y="Price", color="Asset", title=title_text
    )
    fig.update_layout(
        legend_title_text="Commodity Name", hovermode="x unified"
    )

    st.plotly_chart(fig)
