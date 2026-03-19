import streamlit as st
import pandas as pd
import numpy as np
import os
from core.nlp_query_engine import run_nl_query
from core.insight_generator import generate_insights
from core.eda_engine import run_eda
from core.kpi_tracker import compute_kpis
from core.anomaly_detector import detect_anomalies
from core.correlation_engine import compute_correlation
from visualizations.chart_factory import bar_chart, pie_chart, line_chart, scatter_plot

def render_tab_chat(df):
    st.markdown("*Powered by Groq LLaMA3.3-70b · Ask follow-up questions — the AI remembers the conversation.*")

    # Init chat state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "chat_results" not in st.session_state:
        st.session_state["chat_results"] = {}

    if not os.getenv("GROQ_API_KEY"):
        st.warning("⚠️ `GROQ_API_KEY` is not set. Add it to your `.env` file to enable AI queries.")

    # ── Controls row ──────────────────────────────────────────────────────────
    _, ctrl_col = st.columns([8, 1])
    with ctrl_col:
        if st.button("🗑️ Clear", width="content"):
            st.session_state["chat_history"] = []
            st.session_state["chat_results"] = {}
            st.rerun()

    # ── Suggestions (only when chat empty) ────────────────────────────────────
    if not st.session_state["chat_history"]:
        st.markdown("**Suggested questions:**")
        suggestions = [
            "Top 5 products by revenue?",
            "Which region has highest sales?",
            "Show monthly revenue trend",
            "Average discount by category?",
            "Summarize the dataset",
        ]
        sug_cols = st.columns(len(suggestions))
        for i, sug in enumerate(suggestions):
            if sug_cols[i].button(sug, key=f"sug_{i}", width='stretch'):
                st.session_state["_pending_question"] = sug
                st.rerun()

    # ── Message container (renders all history, newest at bottom) ─────────────
    chat_box = st.container(height=560, border=False)
    with chat_box:
        for idx, turn in enumerate(st.session_state["chat_history"]):
            role    = turn["role"]
            content = turn["content"]
            with st.chat_message(role):
                st.markdown(content)
                if role == "assistant" and idx in st.session_state["chat_results"]:
                    extras = st.session_state["chat_results"][idx]
                    pcode       = extras.get("pandas_code", "")
                    rval        = extras.get("result")
                    csug        = extras.get("chart_suggestion", "none")
                    err         = extras.get("error")
                    explanation = extras.get("explanation", "")
                    reason      = extras.get("reason", "")
                    if err and err not in ("Missing API key",):
                        st.error(f"⚠️ {err}")
                    if reason:
                        st.caption(f"🔎 *Operation rationale: {reason}*")
                    if pcode:
                        with st.expander("🔍 View Generated Code"):
                            st.code(pcode, language="python")
                    if isinstance(rval, pd.DataFrame) and not rval.empty:
                        st.dataframe(rval, width='stretch')
                        nr = rval.select_dtypes(include=np.number).columns.tolist()
                        sr = rval.select_dtypes(include="object").columns.tolist()
                        if csug != "none" and nr and sr:
                            try:
                                ck = f"chat_chart_{idx}"
                                if csug == "bar":
                                    st.plotly_chart(bar_chart(rval, sr[0], nr[0]), width='stretch', key=ck)
                                elif csug == "pie":
                                    st.plotly_chart(pie_chart(rval, sr[0], nr[0]), width='stretch', key=ck)
                                elif csug == "line":
                                    st.plotly_chart(line_chart(rval, sr[0], nr[0]), width='stretch', key=ck)
                                elif csug == "scatter" and len(nr) >= 2:
                                    st.plotly_chart(scatter_plot(rval, nr[0], nr[1]), width='stretch', key=ck)
                            except Exception:
                                pass
                    elif isinstance(rval, pd.Series):
                        st.dataframe(rval.to_frame(), width='stretch')
                    elif rval is not None:
                        st.success(f"**Result:** {rval}")
                    if explanation:
                        st.info(f"💡 **Insight:** {explanation}")

    # ── Chat input BELOW the message box ──────────────────────────────────────
    pending  = st.session_state.pop("_pending_question", None)
    question = st.chat_input("Ask a question about your data...", key="chat_input") or pending

    if question:
        api_history = [{"role": t["role"], "content": t["content"]}
                       for t in st.session_state["chat_history"]]
        st.session_state["chat_history"].append({"role": "user", "content": question})

        with st.spinner("Thinking..."):
            resp = run_nl_query(df, question, chat_history=api_history)

        raw_answer  = resp.get("raw_answer", "")
        explanation = resp.get("explanation", "")
        reason      = resp.get("reason", "")
        # Use raw_answer as the chat bubble text; fallback to explanation
        answer      = raw_answer or explanation or "Here are the results:"
        turn_idx    = len(st.session_state["chat_history"])
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})
        st.session_state["chat_results"][turn_idx] = {
            "pandas_code":      resp.get("pandas_code", ""),
            "result":           resp.get("result"),
            "chart_suggestion": resp.get("chart_suggestion", "none"),
            "error":            resp.get("error"),
            "explanation":      explanation,
            "reason":           reason,
        }
        st.rerun()   # re-render so new message appears inside the container above



    # AI Business Insights panel
    st.markdown("---")
    st.markdown("#### 🧠 AI Business Insights")
    st.markdown("*Generate comprehensive AI insights across your entire dataset.*")

    if st.button("✨ Generate AI Insights", type="primary"):
        with st.spinner("Generating insights with Groq LLaMA3..."):
            # Ensure we have the prerequisites
            eda_res = st.session_state["eda_result"] or run_eda(df)
            kpi_res = st.session_state["kpi_cards"] or compute_kpis(df)
            anom_res = st.session_state["anomaly_result"] or detect_anomalies(df)
            corr_res = st.session_state["corr_result"] or compute_correlation(df)

            insights = generate_insights(
                eda_result=eda_res,
                kpi_cards=kpi_res,
                anomaly_summary=anom_res.get("summary", {}),
                correlation_pairs=corr_res.get("top_pairs", []),
                dataset_name=st.session_state["dataset_name"],
            )
            st.session_state["insights"] = insights

    if st.session_state["insights"]:
        severity_colors = {"high": "insight-high", "medium": "insight-medium", "low": "insight-low"}
        for insight in st.session_state["insights"]:
            sev = insight.get("severity", "medium")
            css_class = severity_colors.get(sev, "insight-medium")
            st.markdown(f"""
            <div class="{css_class}">
              <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
                    color:{'#EF553B' if sev=='high' else '#FFA15A' if sev=='medium' else '#00CC96'};">
                ● {sev.upper()} PRIORITY
              </span>
              <h4>{insight.get('title', '')}</h4>
              <p>{insight.get('insight', '')}</p>
              <div class="insight-action">💡 {insight.get('action', '')}</div>
            </div>
            """, unsafe_allow_html=True)
