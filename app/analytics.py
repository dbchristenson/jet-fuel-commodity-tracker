from datetime import datetime as dt

import pandas as pd


def data_granularity_and_aggregate_stats(
    freq_selection, agg_method, filtered_assets_df
):
    # Map UI text to Pandas offset aliases
    freq_map = {"Daily": None, "Weekly": "W", "Monthly": "ME"}

    # Map UI text to specific pandas function names
    agg_map = {"Average Price": "mean", "Close Price": "last"}

    if freq_map[freq_selection]:
        # Set the aggregation function dynamically based on the toggle
        func_to_apply = agg_map[agg_method]

        df_plot = (
            filtered_assets_df.set_index("Date")
            .groupby("Asset")["Price"]
            .resample(freq_map[freq_selection])
            .agg(func_to_apply)  # Applies .mean() or .last() dynamically
            .reset_index()
        )
    else:
        # Daily data is already discrete; no aggregation needed
        df_plot = filtered_assets_df

    return df_plot


def calculate_slope_over_time_period(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    start_date: dt,
):
    """
    Calculates the slope of a time series over a specified period.
    """

    values_in_period = df[df[date_col] >= start_date][value_col]

    if len(values_in_period) < 2:
        return None
