from datetime import datetime as dt

import numpy as np
import pandas as pd


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
