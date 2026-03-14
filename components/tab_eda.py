import streamlit as st
import pandas as pd
from core.eda_engine import run_eda
from visualizations.chart_factory import null_heatmap, histogram

def render_tab_eda(df):

    if st.session_state["eda_result"] is None:
        if st.button("🔍 Run EDA", width="content"):
            with st.spinner("Running EDA..."):
                st.session_state["eda_result"] = run_eda(df)

    eda = st.session_state["eda_result"]
    if eda:
        col_types = eda.get("column_types", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Numeric Cols", len(col_types.get("numeric", [])))
        c2.metric("Categorical Cols", len(col_types.get("categorical", [])))
        c3.metric("Datetime Cols", len(col_types.get("datetime", [])))
        c4.metric("Total Nulls", f"{eda.get('total_nulls', 0):,}")

        # Null heatmap
        if eda.get("null_map"):
            st.markdown("#### Missing Values")
            st.plotly_chart(null_heatmap(eda["null_map"]), width='stretch', key="eda_null_heatmap")

        # Numeric stats
        if eda.get("numeric_stats"):
            st.markdown("#### Numeric Column Statistics")
            stats_list = []
            for col, s in eda["numeric_stats"].items():
                stats_list.append({
                    "Column": col, "Count": s["count"], "Mean": s["mean"],
                    "Median": s["median"], "Std": s["std"], "Min": s["min"],
                    "Max": s["max"], "Skewness": s["skewness"], "Kurtosis": s["kurtosis"],
                    "Nulls": s["null_count"],
                })
            st.dataframe(pd.DataFrame(stats_list), width="stretch")

            st.markdown("#### Distribution Explorer")
            num_col = st.selectbox("Select column for histogram", col_types.get("numeric", []))
            if num_col:
                st.plotly_chart(histogram(df, num_col), width='stretch', key="eda_hist")

        # Categorical stats
        if eda.get("categorical_summary"):
            st.markdown("#### Categorical Column Summaries")
            for col, info in eda["categorical_summary"].items():
                with st.expander(f"`{col}` — {info['unique_count']} unique values"):
                    vc_df = pd.DataFrame(info["top_values"].items(), columns=["Value", "Count"])
                    st.dataframe(vc_df, width="stretch")
    else:
        st.info("Click `Run EDA` to generate analysis.")
