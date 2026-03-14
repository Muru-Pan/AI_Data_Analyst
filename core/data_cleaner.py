"""
data_cleaner.py — Cleans and preprocesses a DataFrame.
"""

import pandas as pd
import numpy as np


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Performs:
    - Duplicate row removal
    - Missing value reporting
    - Whitespace stripping from strings
    - Automatic date column inference
    - Type coercion for numeric-looking string columns

    Returns (cleaned_df, cleaning_report_dict).
    """
    report = {}
    original_shape = df.shape
    df = df.copy()

    # 1. Remove duplicate rows
    dup_count = df.duplicated().sum()
    df.drop_duplicates(inplace=True)
    report["duplicates_removed"] = int(dup_count)

    # 2. Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns.tolist()
    for col in str_cols:
        df[col] = df[col].str.strip()
    report["string_cols_stripped"] = str_cols

    # 3. Try to infer datetime columns
    date_cols_converted = []
    for col in df.columns:
        if df[col].dtype == object:
            try:
                converted = pd.to_datetime(df[col], errors="coerce")
                # Only convert if >80% of values parse successfully
                if converted.notna().mean() > 0.8:
                    df[col] = converted
                    date_cols_converted.append(col)
            except Exception:
                pass
    report["date_cols_inferred"] = date_cols_converted

    # 4. Coerce numeric-looking string columns
    numeric_coerced = []
    for col in df.select_dtypes(include="object").columns:
        coerced = pd.to_numeric(df[col], errors="coerce")
        if coerced.notna().mean() > 0.9:
            df[col] = coerced
            numeric_coerced.append(col)
    report["numeric_cols_coerced"] = numeric_coerced

    # 5. Null value report per column
    null_report = df.isnull().sum()
    null_report = null_report[null_report > 0].to_dict()
    report["null_counts"] = {k: int(v) for k, v in null_report.items()}
    report["total_nulls"] = int(df.isnull().sum().sum())

    report["original_shape"] = original_shape
    report["cleaned_shape"] = df.shape

    return df, report


def fill_missing(df: pd.DataFrame, strategy: str = "none") -> pd.DataFrame:
    """
    Fill missing values.
    strategy: 'mean', 'median', 'mode', 'ffill', 'bfill', 'drop', or 'none'
    """
    df = df.copy()
    if strategy == "mean":
        numeric_cols = df.select_dtypes(include=np.number).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    elif strategy == "median":
        numeric_cols = df.select_dtypes(include=np.number).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    elif strategy == "mode":
        for col in df.columns:
            mode = df[col].mode()
            if not mode.empty:
                df[col] = df[col].fillna(mode[0])
    elif strategy == "ffill":
        df = df.ffill()
    elif strategy == "bfill":
        df = df.bfill()
    elif strategy == "drop":
        df = df.dropna()
    return df
