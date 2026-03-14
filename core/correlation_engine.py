"""
correlation_engine.py — Correlation matrix and feature importance analysis.
"""

import pandas as pd
import numpy as np


def compute_correlation(df: pd.DataFrame, method: str = "pearson") -> dict:
    """
    Computes Pearson or Spearman correlation matrix for numeric columns.
    Returns corr_matrix (DataFrame) and top N correlated pairs.
    """
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.shape[1] < 2:
        return {"corr_matrix": pd.DataFrame(), "top_pairs": [], "method": method}

    corr = numeric_df.corr(method=method)

    # Extract top correlated pairs (excluding self-correlations)
    pairs = []
    cols = corr.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append({
                "col_a": cols[i],
                "col_b": cols[j],
                "correlation": round(float(corr.iloc[i, j]), 4),
                "abs_correlation": round(abs(float(corr.iloc[i, j])), 4),
            })

    pairs.sort(key=lambda x: x["abs_correlation"], reverse=True)

    return {
        "corr_matrix": corr,
        "top_pairs": pairs[:20],
        "method": method,
    }


def compute_feature_importance(df: pd.DataFrame, target_col: str) -> dict:
    """
    Uses Random Forest to rank feature importance against a numeric target column.
    Returns a dict of {feature: importance_score}.
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder

    numeric_df = df.select_dtypes(include=np.number).copy()

    if target_col not in numeric_df.columns:
        return {"error": f"Target column '{target_col}' is not numeric."}

    feature_cols = [c for c in numeric_df.columns if c != target_col]
    if not feature_cols:
        return {"error": "Insufficient numeric feature columns."}

    X = numeric_df[feature_cols].fillna(0)
    y = numeric_df[target_col].fillna(0)

    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X, y)

    importance = dict(zip(feature_cols, rf.feature_importances_))
    importance = {k: round(float(v), 6) for k, v in sorted(
        importance.items(), key=lambda x: x[1], reverse=True
    )}
    return importance
