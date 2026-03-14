"""
data_loader.py — Loads CSV, Excel files and fetches tables from Supabase.
"""

import pandas as pd
import io
import os
from dotenv import load_dotenv

load_dotenv()


def load_file(file_source) -> tuple[pd.DataFrame, dict]:
    """
    Load a CSV or Excel file.
    file_source: str (path) or file-like object (Streamlit UploadedFile).
    Returns (DataFrame, metadata_dict).
    """
    if isinstance(file_source, str):
        name = file_source
        if name.endswith(".csv"):
            df = pd.read_csv(file_source)
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_source)
        else:
            raise ValueError(f"Unsupported file type: {name}")
    else:
        # Streamlit UploadedFile
        name = file_source.name
        content = file_source.read()
        if name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise ValueError(f"Unsupported file type: {name}")

    metadata = {
        "source": name,
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 3),
    }
    return df, metadata


def list_supabase_tables() -> list[str]:
    """
    Return a list of table names from the connected Supabase project.
    Requires SUPABASE_URL and SUPABASE_KEY in environment.
    """
    from supabase import create_client
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set.")
    client = create_client(url, key)
    # Query information_schema for public tables
    result = client.rpc("pg_catalog_tables_public", {}).execute()
    tables = [row["tablename"] for row in result.data] if result.data else []
    return tables


def load_supabase_table(table_name: str, limit: int = 5000) -> tuple[pd.DataFrame, dict]:
    """
    Fetch up to `limit` rows from a Supabase table as a DataFrame.
    """
    from supabase import create_client
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set.")
    client = create_client(url, key)
    response = client.table(table_name).select("*").limit(limit).execute()
    df = pd.DataFrame(response.data)
    metadata = {
        "source": f"supabase:{table_name}",
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 3),
    }
    return df, metadata
