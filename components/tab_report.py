import streamlit as st
import pandas as pd
import numpy as np
from core.report_generator import generate_html_report
from core.eda_engine import run_eda
from core.kpi_tracker import compute_kpis
from core.anomaly_detector import detect_anomalies
from core.correlation_engine import compute_correlation
from visualizations.chart_factory import histogram, heatmap, anomaly_scatter

def render_tab_report(df):
    st.markdown("Generate a rich HTML report with all analyses, charts, and AI insights.")

    include_charts = st.multiselect(
        "Charts to include in report",
        ["Distribution Histograms", "Correlation Heatmap", "KPI Trends", "Anomaly Scatter"],
        default=["Distribution Histograms", "Correlation Heatmap"],
    )

    if st.button("📄 Generate Report", type="primary", width="content"):
        with st.spinner("Generating report..."):
            # Gather all analyses
            eda_res = st.session_state["eda_result"] or run_eda(df)
            kpi_res = st.session_state["kpi_cards"] or compute_kpis(df)
            anom_res = st.session_state["anomaly_result"] or detect_anomalies(df)
            corr_res = st.session_state["corr_result"] or compute_correlation(df)
            insights = st.session_state["insights"] or []

            # Build figures list
            figs = []
            numeric_cols_r = df.select_dtypes(include=np.number).columns.tolist()
            if "Distribution Histograms" in include_charts:
                for col in numeric_cols_r[:3]:
                    figs.append(histogram(df, col))
            if "Correlation Heatmap" in include_charts and not corr_res["corr_matrix"].empty:
                figs.append(heatmap(corr_res["corr_matrix"]))
            if "Anomaly Scatter" in include_charts and anom_res.get("flag_columns"):
                for col in numeric_cols_r[:2]:
                    fc = f"{col}_iqr_flag"
                    if fc in anom_res["anomaly_rows"].columns:
                        try:
                            joined = df[[col]].join(anom_res["anomaly_rows"][[fc]], how="left")
                            joined[fc] = joined[fc].fillna(False).astype(bool)
                            figs.append(anomaly_scatter(joined, col, fc))
                        except Exception:
                            pass

            html_content = generate_html_report(
                dataset_name=st.session_state["dataset_name"],
                eda_result=eda_res,
                kpi_cards=kpi_res,
                anomaly_result=anom_res,
                insights=insights,
                figures=figs,
            )
            st.session_state["report_html"] = html_content
            st.success("✅ Report generated!")

    if "report_html" in st.session_state and st.session_state.get("report_html"):
        st.download_button(
            "⬇️ Download HTML Report",
            data=st.session_state["report_html"],
            file_name=f"ai_analysis_{st.session_state['dataset_name'].replace(' ', '_')}.html",
            mime="text/html",
            width="content",
        )
        with st.expander("👁️ Preview Report"):
            st.components.v1.html(st.session_state["report_html"], height=800, scrolling=True)
    else:
        st.info("Click `Generate Report` to build and download your analytics report.")
