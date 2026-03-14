import streamlit as st
import pandas as pd
import numpy as np
from core.correlation_engine import compute_correlation, compute_feature_importance
from visualizations.chart_factory import heatmap, bar_chart

def render_tab_correlations(df):

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns for correlation analysis.")
    else:
        method = st.radio("Correlation method", ["pearson", "spearman"], horizontal=True)

        if st.session_state["corr_result"] is None:
            if st.button("🔄 Compute Correlations"):
                with st.spinner("Computing correlations..."):
                    st.session_state["corr_result"] = compute_correlation(df, method)
        elif st.button("🔄 Recompute Correlations"):
            with st.spinner("Computing correlations..."):
                st.session_state["corr_result"] = compute_correlation(df, method)

        corr_res = st.session_state["corr_result"]
        if corr_res and not corr_res["corr_matrix"].empty:
            st.plotly_chart(heatmap(corr_res["corr_matrix"]), width='stretch', key="corr_heatmap")

            st.markdown("#### Top Correlated Pairs")
            pairs_df = pd.DataFrame(corr_res["top_pairs"])
            if not pairs_df.empty:
                st.dataframe(pairs_df, width="stretch")

        # Feature importance
        st.markdown("---")
        st.markdown("#### 🌲 Feature Importance (Random Forest)")
        target_col = st.selectbox("Select target column", numeric_cols)
        if st.button("Compute Feature Importance"):
            with st.spinner("Training Random Forest..."):
                importance = compute_feature_importance(df, target_col)
            if "error" in importance:
                st.error(importance["error"])
            else:
                imp_df = pd.DataFrame(importance.items(), columns=["Feature", "Importance"])
                st.plotly_chart(bar_chart(imp_df, "Feature", "Importance"), width='stretch', key="corr_importance_bar")
                st.dataframe(imp_df, width="stretch")
