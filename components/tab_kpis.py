import streamlit as st
import pandas as pd
from core.kpi_tracker import compute_kpis
from core.trend_analyzer import analyze_trends, find_date_columns
from visualizations.chart_factory import trend_line_chart

def render_tab_kpis(df):

    date_cols = find_date_columns(df)
    date_col_kpi = st.selectbox("Date column (for growth calc)", ["None"] + date_cols)
    date_col_kpi = None if date_col_kpi == "None" else date_col_kpi

    if st.button("📊 Compute KPIs", width="content"):
        with st.spinner("Computing KPIs..."):
            kpi_cards = compute_kpis(df, date_col=date_col_kpi)
            st.session_state["kpi_cards"] = kpi_cards

    kpis = st.session_state["kpi_cards"]
    if kpis:
        st.markdown("#### Key Metrics")
        n_cols = min(len(kpis), 4)
        metric_cols = st.columns(n_cols)
        for idx, kpi in enumerate(kpis):
            with metric_cols[idx % n_cols]:
                delta = f"{kpi['growth_pct']:+.1f}%" if kpi.get("growth_pct") is not None else None
                st.metric(
                    label=kpi["name"].replace("_", " ").title(),
                    value=f"{kpi['total']:,.0f}",
                    delta=delta,
                )

        st.markdown("#### KPI Details")
        kpi_df = pd.DataFrame(kpis)
        st.dataframe(kpi_df, width="stretch")

        # Trend analysis for KPI columns
        if date_cols:
            st.markdown("---")
            st.markdown("#### 📈 Trend Analysis")
            date_col_trend = st.selectbox("Date column", date_cols, key="trend_date")
            freq = st.selectbox("Frequency", ["D", "W", "M", "Q", "Y"],
                                format_func=lambda x: {"D":"Daily","W":"Weekly","M":"Monthly","Q":"Quarterly","Y":"Yearly"}[x])
            kpi_col_names = [k["name"] for k in kpis]

            if st.button("📈 Analyze Trends"):
                with st.spinner("Analyzing trends..."):
                    trends = analyze_trends(df, date_col_trend, kpi_col_names, freq)
                if "error" in trends:
                    st.error(trends["error"])
                else:
                    for col_name, trend_info in trends.items():
                        st.markdown(f"**{col_name}** — Trend: {trend_info['trend']}")
                        st.plotly_chart(
                            trend_line_chart(trend_info["grouped"], col_name, trend_info["freq_label"]),
                            width='stretch',
                            key=f"kpi_trend_{col_name}",
                        )
    else:
        st.info("Click `Compute KPIs` to auto-discover and analyze business metrics.")
