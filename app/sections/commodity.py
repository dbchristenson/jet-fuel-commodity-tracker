import json
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
    Clean up the Excel dataframe:
    1. Convert 'Date' to datetime.
    2. Rename the price column to a standard 'Price'.
    3. Add a metadata column for the 'Asset'.
    """
    df["Date"] = pd.to_datetime(df["Date"])
    # Rename the value column (index 1) to 'Price'
    df.rename(columns={df.columns[1]: "Price"}, inplace=True)
    df["Asset"] = commodity_name
    return df


def load_spot_prices_json(file_path: Path) -> pd.DataFrame:
    """
    Load and transform the EIA spot prices JSON data.
    Expected JSON keys per record: 'period', 'value', 'series-description'
    """
    # Keys are lowercased here to match the normalized column data later
    JSON_ASSET_NAME_MAP = {
        "u.s. gulf coast kerosene-type jet fuel spot price fob (dollars per gallon)": "Gulf Coast Jet Fuel",  # noqa E501
        "u.s. gulf coast ultra-low sulfur no 2 diesel spot price (dollars per gallon)": "Gulf Coast No 2 Diesel",  # noqa E501
        "u.s. gulf coast conventional gasoline regular spot price fob (dollars per gallon)": "Gulf Coast Regular Gasoline",  # noqa E501
    }

    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # 1. Normalize Columns
        rename_map = {"period": "Date", "value": "Price"}
        df.rename(columns=rename_map, inplace=True)

        # 2. Determine Initial Asset Name
        if "series-description" in df.columns:
            df["Asset"] = df["series-description"]
        elif "series" in df.columns:
            df["Asset"] = df["series"]
        else:
            df["Asset"] = "Unknown Commodity"

        # 3. Apply Name Mapping
        # We create a temporary series of lowercased names to lookup in the map
        mapped_assets = (
            df["Asset"]
            .astype(str)
            .str.lower()
            .str.strip()
            .map(JSON_ASSET_NAME_MAP)
        )
        # We fill NaNs with the original (non-lowercased) names
        df["Asset"] = mapped_assets.fillna(df["Asset"])

        # 4. Type Conversion
        df["Date"] = pd.to_datetime(df["Date"])
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

        return df[["Date", "Price", "Asset"]]

    except Exception as e:
        st.warning(f"Error loading JSON data from {file_path.name}: {e}")
        return pd.DataFrame()


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
    """
    Grab commodity data.
    PRIORITY: Checks for 'spot_prices.json' first.
    If JSON exists and is valid, returns THAT ONLY (ignoring Excel).
    If JSON fails or is missing, falls back to Excel files.
    """
    data_dir = Path(__file__).parents[2] / "data"

    if not data_dir.exists():
        st.error(f"Data directory not found at {data_dir}")
        return pd.DataFrame(), []

    # ---------------------------------------------------------
    # 1. Try Loading JSON First (The "Truth" Source)
    # ---------------------------------------------------------
    json_path = data_dir / "spot_prices.json"
    if json_path.exists():
        json_df = load_spot_prices_json(json_path)
        if not json_df.empty:
            # If we successfully loaded JSON, we transform and RETURN.
            # We do NOT load Excel files to avoid duplicates.
            commodity_df = transform_commodity_df(json_df)
            assets = sorted(commodity_df["Asset"].unique().tolist())
            return commodity_df, assets

    # ---------------------------------------------------------
    # 2. Fallback: Load Excel Files (Only if JSON missing/empty)
    # ---------------------------------------------------------
    commodity_data = []
    assets = []
    data_children = os.listdir(data_dir)

    for child in data_children:
        if child.endswith(".xlsx") and "commodity_" in child:
            commodity_name = child.replace("commodity_", "").replace(
                "_prices.xlsx", ""
            )
            file_path = data_dir / child

            try:
                df = pd.read_excel(file_path, skiprows=2, sheet_name="Data 1")
                df = clean_df(df, commodity_name=commodity_name)

                if not df.empty:
                    commodity_data.append(df)
                    if commodity_name not in assets:
                        assets.append(commodity_name)

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
    min_value = int(commodity_df["Year"].min())
    max_value = int(commodity_df["Year"].max())

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
        # Default to first asset if available
        default_asset = assets[0] if assets else None

        selected_assets = st.multiselect(
            "Which assets would you like to view?",
            assets,
            default=default_asset,
            # removed str.capitalize to respect the exact formatting in the map
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

    st.header("US Commodity Prices ($/Gallon)", divider="gray")
    title_text = f"{freq_selection} Commodity Prices ({agg_method})"

    fig = px.line(
        df_plot, x="Date", y="Price", color="Asset", title=title_text
    )
    fig.update_layout(
        legend_title_text="Commodity Name", hovermode="x unified"
    )
    fig.update_yaxes(title_text="Dollars per Gallon")

    st.plotly_chart(fig)
