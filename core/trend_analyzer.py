"""
trend_analyzer.py — Time-series trend detection and period aggregation.
"""

import pandas as pd
import numpy as np


def find_date_columns(df: pd.DataFrame) -> list[str]:
    """Return all datetime-typed columns in the DataFrame."""
    return df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()


def analyze_trends(
    df: pd.DataFrame,
    date_col: str,
    value_cols: list[str] | None = None,
    freq: str = "M"
) -> dict:
    """
    Groups a DataFrame by the specified date column and frequency, then
    computes totals, rolling averages, and trend direction per value column.

    freq: 'D' (day), 'W' (week), 'M' (month), 'Q' (quarter), 'Y' (year)
    value_cols: numeric columns to analyze; defaults to all numeric cols.

    Returns a dict of {col: {"grouped": DataFrame, "trend": str, "rolling_avg": Series}}
    """
    if date_col not in df.columns:
        return {"error": f"Date column '{date_col}' not found."}

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    df = df.sort_values(date_col)

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if value_cols:
        numeric_cols = [c for c in value_cols if c in numeric_cols]

    if not numeric_cols:
        return {"error": "No numeric columns available for trend analysis."}

    results = {}
    # pandas 2.2+ requires 'ME'/'QE'/'YE' instead of 'M'/'Q'/'Y'
    freq_alias_map = {"D": "D", "W": "W", "M": "ME", "Q": "QE", "Y": "YE"}
    freq_label = {"D": "Daily", "W": "Weekly", "M": "Monthly", "Q": "Quarterly", "Y": "Yearly"}.get(freq, freq)
    freq_safe = freq_alias_map.get(freq, freq)

    for col in numeric_cols:
        temp = df[[date_col, col]].dropna()
        if len(temp) < 3:
            continue
        grouped = temp.set_index(date_col)[col].resample(freq_safe).sum().reset_index()
        grouped.columns = ["period", col]

        # Rolling average (window = min(3, len))
        window = min(3, len(grouped))
        grouped["rolling_avg"] = grouped[col].rolling(window=window, min_periods=1).mean().round(2)

        # Trend direction: compare first vs last half
        mid = len(grouped) // 2
        if mid > 0:
            first = grouped[col].iloc[:mid].mean()
            last = grouped[col].iloc[mid:].mean()
            if last > first * 1.05:
                trend = "📈 Upward"
            elif last < first * 0.95:
                trend = "📉 Downward"
            else:
                trend = "➡️ Flat"
        else:
            trend = "➡️ Flat"

        results[col] = {
            "grouped": grouped,
            "trend": trend,
            "freq_label": freq_label,
        }

    return results
