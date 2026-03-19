import streamlit as st
import pandas as pd
from core.data_cleaner import clean_dataframe, fill_missing

def render_tab_overview(df, df_raw):

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", f"{df.isnull().sum().sum():,}")
    col4.metric("Duplicate Rows", f"{df.duplicated().sum():,}")

    st.markdown("#### Column Schema")
    schema_df = pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.astype(str).values,
        "Non-Null": df.notnull().sum().values,
        "Null Count": df.isnull().sum().values,
        "Null %": (df.isnull().sum().values / len(df) * 100).round(2),
        "Unique Values": [df[c].nunique() for c in df.columns],
        "Sample Value": [str(df[c].dropna().iloc[0]) if df[c].notnull().any() else "N/A" for c in df.columns],
    })
    st.dataframe(schema_df, width='stretch')

    st.markdown("#### 🔧 Data Cleaning")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        fill_strategy = st.selectbox(
            "Missing value strategy",
            ["none", "mean", "median", "mode", "ffill", "bfill", "drop"],
            help="How to handle null values after cleaning"
        )
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        run_clean = st.button("🧹 Clean Dataset", width='stretch')

    if run_clean:
        with st.spinner("Cleaning dataset..."):
            df_cleaned, report = clean_dataframe(df_raw)
            df_cleaned = fill_missing(df_cleaned, fill_strategy)
            st.session_state["df_clean"] = df_cleaned
            st.session_state["cleaning_report"] = report
            st.session_state["eda_result"] = None
        st.success("Dataset cleaned successfully!")
        df = df_cleaned

    if st.session_state["cleaning_report"]:
        report = st.session_state["cleaning_report"]
        with st.expander("📋 Cleaning Report", expanded=True):
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Duplicates Removed", report.get("duplicates_removed", 0))
            rc2.metric("Date Cols Inferred", len(report.get("date_cols_inferred", [])))
            rc3.metric("Numeric Cols Coerced", len(report.get("numeric_cols_coerced", [])))
            if report.get("null_counts"):
                st.markdown("**Remaining nulls per column:**")
                null_df = pd.DataFrame(report["null_counts"].items(), columns=["Column", "Null Count"])
                st.dataframe(null_df, width='stretch')

    st.markdown("#### Preview (first 50 rows)")
    st.dataframe(df.head(50), width='stretch')
