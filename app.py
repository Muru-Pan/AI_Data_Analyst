"""
app.py — AI Data Analyst — Main Streamlit Dashboard
"""

import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataMind — AI Data Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
with open("assets/style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Core imports ─────────────────────────────────────────────────────────────
from core.data_loader import load_file, load_supabase_table

# ── Component imports ────────────────────────────────────────────────────────
from components.auth import render_auth
from components.tab_overview import render_tab_overview
from components.tab_eda import render_tab_eda
from components.tab_visualize import render_tab_visualize
from components.tab_correlations import render_tab_correlations
from components.tab_anomalies import render_tab_anomalies
from components.tab_kpis import render_tab_kpis
from components.tab_chat import render_tab_chat
from components.tab_report import render_tab_report

def init_state():
    defaults = {
        "authenticated": False,
        "username": None,
        "df": None,
        "df_clean": None,
        "dataset_name": "",
        "cleaning_report": None,
        "eda_result": None,
        "kpi_cards": None,
        "anomaly_result": None,
        "corr_result": None,
        "insights": None,
        "report_html": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── AUTHENTICATION ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    render_auth()
    st.stop()

# Navbar
nav_c1, nav_c2, nav_c3 = st.columns([2, 6, 2])
with nav_c1:
    st.markdown("<div class='brand' style='padding-top:.5rem;'>Data<span>Mind</span></div>", unsafe_allow_html=True)
with nav_c3:
    st.markdown(f"<div class='nav-user' style='text-align:right;padding-top:.7rem;'>Signed in as <strong style='color:#4f46e5;'>{st.session_state['username']}</strong></div>", unsafe_allow_html=True)
    if st.button("Sign Out", key="nav_logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["df"] = None
        st.rerun()

st.markdown("<hr style='margin:.2rem 0 1.5rem;border-color:rgba(79,70,229,0.1);'>", unsafe_allow_html=True)

# MAIN CONTENT
if st.session_state.get("df") is not None:
    df_active = st.session_state["df_clean"] if st.session_state["df_clean"] is not None else st.session_state["df"]
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
        margin-bottom:1.5rem;color:#64748b;font-size:.95rem;font-weight:500;
        font-family:'Inter',sans-serif; background: #f8fafc; padding: 1rem 1.5rem; border-radius: 16px; border: 1px solid #e2e8f0;">
        <div>Dataset: <span style="color:#4f46e5;font-weight:700;">{st.session_state['dataset_name']}</span></div>
        <div>Shape: <span style="color:#4f46e5;font-weight:700;">{df_active.shape[0]:,} rows x {df_active.shape[1]} cols</span></div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state["df"] is None:
    st.markdown("""
    <div class="hero-wrap">
      <div class="hero-badge">Intelligence at Scale</div>
      <h1 class="hero-h1">Business Data,<br><span class="grad">Perfectly Analyzed.</span></h1>
      <p class="hero-sub">
        Upload your datasets and unlock instant <strong>automated insights</strong>, 
        <strong>anomaly detection</strong>, and <strong>interactive visualizations</strong> with AI.
      </p>
    </div>
    <div class="feature-grid">
      <div class="feat-card" style="animation-delay:.0s">
        <div class="feat-icon">📊</div>
        <div class="feat-title">Smart EDA</div>
        <div class="feat-desc">Instant statistical profiling, data cleaning, and schema mapping.</div>
      </div>
      <div class="feat-card" style="animation-delay:.1s">
        <div class="feat-icon">🎯</div>
        <div class="feat-title">AI Insights</div>
        <div class="feat-desc">Powerful LLM patterns to generate human-readable recommendations.</div>
      </div>
      <div class="feat-card" style="animation-delay:.2s">
        <div class="feat-icon">🔍</div>
        <div class="feat-title">Anomaly Detection</div>
        <div class="feat-desc">Advanced Z-score and IQR methods to find every outlier.</div>
      </div>
      <div class="feat-card" style="animation-delay:.3s">
        <div class="feat-icon">⚡</div>
        <div class="feat-title">Fast Reports</div>
        <div class="feat-desc">Convert complex data into beautiful interactive dashboards instantly.</div>
      </div>
    </div>
    <div class="section-divider"></div>
    <div class="section-title">Load Your Dataset</div>
    <div class="section-sub">Get your full analytics dashboard in under 10 seconds.</div>
    """, unsafe_allow_html=True)

    upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
    with upload_col2:
        st.markdown("<div class='upload-card'>", unsafe_allow_html=True)
        source_tab = st.radio("source", ["Upload File"], horizontal=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)

        if source_tab == "Upload File":
            uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
            if uploaded and st.button("Load Dataset", width="stretch"):
                with st.spinner("Loading..."):
                    df, meta = load_file(uploaded)
                    st.session_state["df"] = df
                    st.session_state["dataset_name"] = uploaded.name
                    st.session_state["df_clean"] = None
                    st.session_state["eda_result"] = None
                    st.session_state["kpi_cards"] = None
                    st.session_state["anomaly_result"] = None
                    st.session_state["corr_result"] = None
                    st.session_state["insights"] = None
                st.success(f"Loaded {meta['shape'][0]:,} rows x {meta['shape'][1]} cols")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="trust-bar">
      <div class="trust-item">100% Local</div>
      <div class="trust-item">CSV &middot; Excel</div>
      <div class="trust-item">Groq LLaMA 3.3 70B</div>
      <div class="trust-item">Instant Analysis</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


df_raw = st.session_state["df"]
df = st.session_state["df_clean"] if st.session_state["df_clean"] is not None else df_raw.copy()

tabs = st.tabs([
    "Overview",
    "EDA & Stats",
    "Visualize",
    "Correlations",
    "Anomalies",
    "KPIs",
    "AI Query",
    "Report",
])

with tabs[0]:
    render_tab_overview(df, df_raw)
with tabs[1]:
    render_tab_eda(df)
with tabs[2]:
    render_tab_visualize(df)
with tabs[3]:
    render_tab_correlations(df)
with tabs[4]:
    render_tab_anomalies(df)
with tabs[5]:
    render_tab_kpis(df)
with tabs[6]:
    render_tab_chat(df)
with tabs[7]:
    render_tab_report(df)
