"""
eda_engine.py — Automated Exploratory Data Analysis engine.
"""

import pandas as pd
import numpy as np
from scipy import stats


def run_eda(df: pd.DataFrame) -> dict:
    """
    Performs comprehensive EDA on a DataFrame and returns a structured results dict.
    """
    result = {}

    # Column classification
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    bool_cols = df.select_dtypes(include="bool").columns.tolist()

    result["column_types"] = {
        "numeric": numeric_cols,
        "categorical": categorical_cols,
        "datetime": datetime_cols,
        "boolean": bool_cols,
    }

    # Basic summary
    result["shape"] = df.shape
    result["total_nulls"] = int(df.isnull().sum().sum())
    result["null_pct"] = round(result["total_nulls"] / (df.shape[0] * df.shape[1]) * 100, 2)

    # Extended numeric statistics
    numeric_stats = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        skew = round(float(series.skew()), 4)
        kurt = round(float(series.kurtosis()), 4)
        mode_result = series.mode()
        mode_val = float(mode_result.iloc[0]) if not mode_result.empty else None
        numeric_stats[col] = {
            "count": int(series.count()),
            "mean": round(float(series.mean()), 4),
            "median": round(float(series.median()), 4),
            "std": round(float(series.std()), 4),
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "q25": round(float(series.quantile(0.25)), 4),
            "q75": round(float(series.quantile(0.75)), 4),
            "skewness": skew,
            "kurtosis": kurt,
            "mode": mode_val,
            "null_count": int(df[col].isnull().sum()),
        }
    result["numeric_stats"] = numeric_stats

    # Categorical value counts (top 10 per column)
    cat_summary = {}
    for col in categorical_cols:
        vc = df[col].value_counts().head(10)
        cat_summary[col] = {
            "unique_count": int(df[col].nunique()),
            "top_values": vc.to_dict(),
            "null_count": int(df[col].isnull().sum()),
        }
    result["categorical_summary"] = cat_summary

    # Datetime summary
    dt_summary = {}
    for col in datetime_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        dt_summary[col] = {
            "min": str(series.min()),
            "max": str(series.max()),
            "range_days": (series.max() - series.min()).days,
            "null_count": int(df[col].isnull().sum()),
        }
    result["datetime_summary"] = dt_summary

    # Null heatmap data (null count per column, sorted descending)
    null_map = df.isnull().sum().sort_values(ascending=False)
    result["null_map"] = {k: int(v) for k, v in null_map.items() if v > 0}

    return result
