"""
anomaly_detector.py — Detects outliers using IQR and Z-score methods.
"""

import pandas as pd
import numpy as np
from scipy import stats


def detect_anomalies(
    df: pd.DataFrame,
    method: str = "both",
    z_threshold: float = 3.0
) -> dict:
    """
    Detect outliers in all numeric columns.
    method: 'iqr', 'zscore', or 'both'
    z_threshold: Z-score cutoff (default 3.0)

    Returns:
      {
        "anomaly_rows": DataFrame of flagged rows with reason columns,
        "summary": {col: {iqr_count, zscore_count}},
      }
    """
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        return {"anomaly_rows": pd.DataFrame(), "summary": {}}

    df = df.copy()
    flag_cols = {}  # col -> boolean Series

    summary = {}
    for col in numeric_cols:
        series = df[col].dropna()
        iqr_flags = pd.Series(False, index=df.index)
        zscore_flags = pd.Series(False, index=df.index)

        if method in ("iqr", "both"):
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            iqr_flags = (df[col] < lower) | (df[col] > upper)

        if method in ("zscore", "both"):
            z_scores = np.abs(stats.zscore(df[col].fillna(df[col].median())))
            zscore_flags = pd.Series(z_scores > z_threshold, index=df.index)

        summary[col] = {
            "iqr_outliers": int(iqr_flags.sum()),
            "zscore_outliers": int(zscore_flags.sum()),
        }

        if method == "iqr":
            flag_cols[f"{col}_iqr_flag"] = iqr_flags
        elif method == "zscore":
            flag_cols[f"{col}_zscore_flag"] = zscore_flags
        else:
            flag_cols[f"{col}_iqr_flag"] = iqr_flags
            flag_cols[f"{col}_zscore_flag"] = zscore_flags

    for col_name, series in flag_cols.items():
        df[col_name] = series

    # Rows flagged by at least one column
    flag_series_list = list(flag_cols.values())
    combined_flag = flag_series_list[0]
    for fs in flag_series_list[1:]:
        combined_flag = combined_flag | fs

    anomaly_rows = df[combined_flag].copy()

    return {
        "anomaly_rows": anomaly_rows,
        "anomaly_count": int(combined_flag.sum()),
        "summary": summary,
        "flag_columns": list(flag_cols.keys()),
    }
