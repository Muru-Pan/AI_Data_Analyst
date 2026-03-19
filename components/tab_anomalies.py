import streamlit as st
import pandas as pd
import numpy as np
from core.anomaly_detector import detect_anomalies
from visualizations.chart_factory import anomaly_scatter

def render_tab_anomalies(df):

    method_a = st.radio("Detection method", ["both", "iqr", "zscore"], horizontal=True)
    z_thresh = st.slider("Z-score threshold", 1.5, 5.0, 3.0, 0.1)

    if st.button("🔍 Detect Anomalies", width="content"):
        with st.spinner("Detecting anomalies..."):
            result = detect_anomalies(df, method=method_a, z_threshold=z_thresh)
            st.session_state["anomaly_result"] = result

    anom_res = st.session_state["anomaly_result"]
    if anom_res:
        anom_count = anom_res.get("anomaly_count", 0)
        col1, col2 = st.columns(2)
        col1.metric("Anomalous Rows Found", anom_count)
        col2.metric("Anomaly Rate", f"{anom_count / len(df) * 100:.2f}%")

        # Summary table
        if anom_res.get("summary"):
            st.markdown("#### Summary by Column")
            sum_df = pd.DataFrame(anom_res["summary"]).T.reset_index()
            sum_df.columns = ["Column", "IQR Outliers", "Z-Score Outliers"]
            st.dataframe(sum_df, width='stretch')

        # Anomaly scatter charts per column
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        flag_cols = anom_res.get("flag_columns", [])
        for col in numeric_cols[:3]:  # Show first 3 to avoid overload
            iqr_flag_col = f"{col}_iqr_flag"
            if iqr_flag_col in anom_res["anomaly_rows"].columns:
                try:
                    joined = df[[col]].join(anom_res["anomaly_rows"][[iqr_flag_col]], how="left")
                    joined[iqr_flag_col] = joined[iqr_flag_col].fillna(False).infer_objects(copy=False).astype(bool)
                    st.plotly_chart(anomaly_scatter(joined, col, iqr_flag_col), width='stretch', key=f"anom_scatter_{col}")
                except Exception:
                    pass

        if anom_count > 0:
            st.markdown("#### Flagged Rows (sample)")
            display_cols = [c for c in df.columns if c in anom_res["anomaly_rows"].columns]
            if display_cols:
                st.dataframe(anom_res["anomaly_rows"][display_cols].head(50), width='stretch')
    else:
        st.info("Click `Detect Anomalies` to identify outliers.")
