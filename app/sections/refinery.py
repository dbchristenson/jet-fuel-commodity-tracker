import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def transform_refinery_df(df: pd.DataFrame):
    """Add Year and Month columns."""
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    return df


def load_refinery_json(file_path: Path) -> pd.DataFrame:
    """
    Load and transform the EIA refinery utilization JSON data.
    """
    # Keys are lowercased to match normalized column data
    REFINERY_NAME_MAP = {
        "gulf coast (padd 3) refinery net production of distillate fuel oil (thousand barrels per day)": "Gulf Coast Distillate Fuel Oil",  # noqa E501
        "u.s. refinery net production of other conventional motor gasoline (thousand barrels per day)": "U.S. Motor Gasoline (Other Conv.)",  # noqa E501
        "gulf coast (padd 3) refinery net production of conventional motor gasoline (thousand barrels per day)": "Gulf Coast Motor Gasoline (Conv.)",  # noqa E501
        "u.s. refinery net production of commercial kerosene-type jet fuel (thousand barrels per day)": "U.S. Jet Fuel",  # noqa E501
        "gulf coast (padd 3) refinery net production of commercial kerosene-type jet fuel (thousand barrels per day)": "Gulf Coast Jet Fuel",  # noqa E501
        "u.s. refinery net production of distillate fuel oil (thousand barrels per day)": "U.S. Distillate Fuel Oil",  # noqa E501
    }

    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # 1. Normalize Columns
        # EIA API usually returns 'period' for date, 'value' for amount
        rename_map = {"period": "Date", "value": "Production"}
        df.rename(columns=rename_map, inplace=True)

        # 2. Determine Asset Name (Series Description)
        # Fallback to 'series' ID if description is missing
        if "series-description" in df.columns:
            df["Asset"] = df["series-description"]
        elif "series" in df.columns:
            df["Asset"] = df["series"]
        else:
            df["Asset"] = "Unknown Series"

        # 3. Filter for 'Barrels per Day' ONLY
        # We lowercase for consistent filtering, then filter
        df = df[
            df["Asset"]
            .astype(str)
            .str.lower()
            .str.contains("thousand barrels per day")
        ].copy()

        # 4. Apply Name Mapping
        mapped_assets = (
            df["Asset"]
            .astype(str)
            .str.lower()
            .str.strip()
            .map(REFINERY_NAME_MAP)
        )
        # Fill NaNs with original name if mapping fails
        df["Asset"] = mapped_assets.fillna(df["Asset"])

        # 5. Type Conversion
        df["Date"] = pd.to_datetime(df["Date"])
        df["Production"] = pd.to_numeric(df["Production"], errors="coerce")

        return df[["Date", "Production", "Asset"]]

    except Exception as e:
        st.warning(f"Error loading refinery JSON from {file_path.name}: {e}")
        return pd.DataFrame()


@st.cache_data
def get_refinery_data():
    """
    Grab refinery data from JSON.
    """
    data_dir = Path(__file__).parents[2] / "data"
    json_path = data_dir / "refinery_utilization.json"

    if not json_path.exists():
        st.error(f"Refinery data not found at {json_path}")
        return pd.DataFrame(), []

    refinery_df = load_refinery_json(json_path)

    if refinery_df.empty:
        return pd.DataFrame(), []

    refinery_df = transform_refinery_df(refinery_df)
    assets = sorted(refinery_df["Asset"].unique().tolist())

    return refinery_df, assets


# -----------------------------------------------------------------------------
# Main Section Render
# -----------------------------------------------------------------------------


def render_refinery_section():
    """Renders the Refinery Production Visualization Section."""

    # Load Data
    refinery_df, assets = get_refinery_data()

    if refinery_df.empty:
        st.warning("No refinery data available to display.")
        return

    col1a, col2a = st.columns(2)

    # Year Selection
    min_value = int(refinery_df["Year"].min())
    max_value = int(refinery_df["Year"].max())

    with col1a:
        from_year, to_year = st.slider(
            "Filter by Year Range:",
            min_value=min_value,
            max_value=max_value,
            value=[2018, max_value],
            key="refinery_year_slider",
        )

    # Asset Selection
    if not assets:
        st.warning("Select at least one product series")

    with col2a:
        default_asset = assets[1] if assets else None

        selected_assets = st.multiselect(
            "Select Product Series:",
            assets,
            default=default_asset,
            key="refinery_asset_multiselect",
        )

    # Filter the data
    filtered_df = refinery_df[
        (refinery_df["Asset"].isin(selected_assets))
        & (refinery_df["Year"] <= to_year)
        & (from_year <= refinery_df["Year"])
    ].sort_values(by="Date")

    st.write("")

    # Visualization
    st.header("US Refinery Utilization Rates", divider="gray")

    fig = px.line(
        filtered_df,
        x="Date",
        y="Production",
        color="Asset",
        title="Net Production (Thousand Barrels per Day)",
    )

    fig.update_layout(
        legend_title_text="Product",
        hovermode="x unified",
        yaxis_title="Production (MBBL/d)",
    )

    st.plotly_chart(fig)
