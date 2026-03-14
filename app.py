"""
app.py — AI Data Analyst — Main Streamlit Dashboard
"""

import os
import io
import json
import pandas as pd
import numpy as np
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
    st.markdown(f"<div class='nav-user' style='text-align:right;padding-top:.7rem;'>Signed in as <strong style='color:#c084fc;'>{st.session_state['username']}</strong></div>", unsafe_allow_html=True)
    if st.button("Sign Out", key="nav_logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["df"] = None
        st.rerun()

st.markdown("<hr style='margin:.2rem 0 1.5rem;border-color:rgba(160,100,255,.15);'>", unsafe_allow_html=True)

# MAIN CONTENT
if st.session_state.get("df") is not None:
    df_active = st.session_state["df_clean"] if st.session_state["df_clean"] is not None else st.session_state["df"]
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
        margin-bottom:1rem;color:#71717a;font-size:.9rem;font-weight:500;
        font-family:'Inter',sans-serif;">
        <div>Dataset: <span style="color:#c084fc;font-weight:600;">{st.session_state['dataset_name']}</span></div>
        <div>Shape: <span style="color:#c084fc;font-weight:600;">{df_active.shape[0]:,} rows x {df_active.shape[1]} cols</span></div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state["df"] is None:
    st.markdown("""
    <div class="hero-wrap">
      <div class="hero-badge">Powered by Groq LLaMA 3.3 70B</div>
      <h1 class="hero-h1">Business Intelligence,<br><span class="grad">Automated.</span></h1>
      <p class="hero-sub">
        Upload any CSV or Excel &mdash; get <strong>EDA</strong>,
        <strong>anomaly detection</strong>, <strong>KPI tracking</strong>
        and <strong>AI-powered insights</strong> in seconds.
      </p>
    </div>
    <div class="feature-grid">
      <div class="feat-card" style="animation-delay:.0s">
        <div class="feat-icon">&#9881;</div>
        <div class="feat-title">Auto EDA</div>
        <div class="feat-desc">Instant stats, distributions, null analysis and schema profiling.</div>
      </div>
      <div class="feat-card" style="animation-delay:.12s">
        <div class="feat-icon">&#10023;</div>
        <div class="feat-title">AI Insights</div>
        <div class="feat-desc">LLaMA 3.3 generates human-readable business recommendations.</div>
      </div>
      <div class="feat-card" style="animation-delay:.24s">
        <div class="feat-icon">&#9888;</div>
        <div class="feat-title">Anomaly Radar</div>
        <div class="feat-desc">IQR and Z-score outlier detection with visual flagging.</div>
      </div>
      <div class="feat-card" style="animation-delay:.36s">
        <div class="feat-icon">&#9670;</div>
        <div class="feat-title">NL to Chart</div>
        <div class="feat-desc">Ask in plain English. Get instant interactive charts.</div>
      </div>
    </div>
    <div class="section-divider"></div>
    <div class="section-title">Load Your Dataset</div>
    <div class="section-sub">Get your full analytics dashboard in under 10 seconds.</div>
    """, unsafe_allow_html=True)

    upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
    with upload_col2:
        st.markdown("<div class='upload-card'>", unsafe_allow_html=True)
        source_tab = st.radio("source", ["Upload File", "Sample Data", "Supabase"], horizontal=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)

        if source_tab == "Upload File":
            uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
            if uploaded and st.button("Load Dataset", use_container_width=True):
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

        elif source_tab == "Sample Data":
            sample_choice = st.selectbox("Choose sample:", ["sample_sales.csv", "sample_ecommerce.csv"])
            if st.button("Load Sample", use_container_width=True):
                sample_path = os.path.join(os.path.dirname(__file__), "data", sample_choice)
                if os.path.exists(sample_path):
                    with st.spinner("Loading..."):
                        df, meta = load_file(sample_path)
                        st.session_state["df"] = df
                        st.session_state["dataset_name"] = sample_choice
                        st.session_state["df_clean"] = None
                        st.session_state["eda_result"] = None
                        st.session_state["kpi_cards"] = None
                        st.session_state["anomaly_result"] = None
                        st.session_state["corr_result"] = None
                        st.session_state["insights"] = None
                    st.success(f"Loaded {meta['shape'][0]:,} rows x {meta['shape'][1]} cols")
                    st.rerun()
                else:
                    st.error(f"Sample file not found: {sample_path}")

        elif source_tab == "Supabase":
            sb_url = st.text_input("Supabase URL", value=os.getenv("SUPABASE_URL", ""))
            sb_key = st.text_input("Supabase Key", type="password", value=os.getenv("SUPABASE_KEY", ""))
            table_name = st.text_input("Table name")
            if st.button("Load Table", use_container_width=True):
                if sb_url and sb_key and table_name:
                    os.environ["SUPABASE_URL"] = sb_url
                    os.environ["SUPABASE_KEY"] = sb_key
                    try:
                        with st.spinner("Connecting to Supabase..."):
                            df, meta = load_supabase_table(table_name)
                            st.session_state["df"] = df
                            st.session_state["dataset_name"] = f"supabase:{table_name}"
                            st.session_state["df_clean"] = None
                            st.session_state["eda_result"] = None
                        st.success(f"Loaded {meta['shape'][0]:,} rows")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Supabase error: {e}")
                else:
                    st.warning("Please fill all Supabase fields.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="trust-bar">
      <div class="trust-item">100% Local</div>
      <div class="trust-item">CSV &middot; Excel &middot; Supabase</div>
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
