"""
kpi_tracker.py — Auto-detects and computes KPI metrics from a DataFrame.
"""

import pandas as pd
import numpy as np
import re

# Keywords that suggest a column is a KPI candidate
KPI_KEYWORDS = [
    "revenue", "sales", "profit", "amount", "cost", "price",
    "count", "quantity", "units", "total", "income", "spend",
    "budget", "margin", "conversion", "rate", "value", "orders",
    "sessions", "clicks", "impressions", "ctr", "aov",
]


def detect_kpi_columns(df: pd.DataFrame) -> list[str]:
    """
    Returns column names that match KPI keyword patterns and are numeric.
    """
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    kpi_cols = []
    for col in numeric_cols:
        col_lower = col.lower().replace("_", " ").replace("-", " ")
        for kw in KPI_KEYWORDS:
            if re.search(rf"\b{kw}\b", col_lower):
                kpi_cols.append(col)
                break
    # Fallback: if no keyword match, return all numeric cols
    return kpi_cols if kpi_cols else numeric_cols


def compute_kpis(df: pd.DataFrame, date_col: str | None = None) -> list[dict]:
    """
    Computes KPI cards for detected KPI columns.
    Each card: {name, total, mean, min, max, growth_pct (if date available)}
    """
    kpi_cols = detect_kpi_columns(df)
    kpi_cards = []

    for col in kpi_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        card = {
            "name": col,
            "total": round(float(series.sum()), 2),
            "mean": round(float(series.mean()), 2),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "count": int(series.count()),
            "growth_pct": None,
        }

        # Compute period-over-period growth if date column available
        if date_col and date_col in df.columns:
            try:
                dated = df[[date_col, col]].dropna()
                dated = dated.sort_values(date_col)
                mid = len(dated) // 2
                first_half_sum = dated.iloc[:mid][col].sum()
                second_half_sum = dated.iloc[mid:][col].sum()
                if first_half_sum != 0:
                    growth = ((second_half_sum - first_half_sum) / abs(first_half_sum)) * 100
                    card["growth_pct"] = round(float(growth), 2)
            except Exception:
                pass

        kpi_cards.append(card)

    return kpi_cards
