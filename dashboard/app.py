"""
Fraud Detection & Risk Operations Platform — Streamlit Dashboard
Main entry point. Handles navigation and shared state.
"""

import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

st.set_page_config(
    page_title="Fraud Risk Operations Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Bootstrap: build the database on first run (e.g. fresh Streamlit Cloud deploy) ──
DB_PATH  = os.path.join(PROJECT_ROOT, "database", "fraud_platform.duckdb")
KPI_PATH = os.path.join(PROJECT_ROOT, "data", "outputs", "executive_kpis.json")

if not os.path.exists(DB_PATH) or not os.path.exists(KPI_PATH):
    with st.spinner("First-time setup: building the fraud database (~15s)..."):
        import importlib.util

        run_pipeline_path = os.path.join(PROJECT_ROOT, "etl", "run_pipeline.py")
        spec = importlib.util.spec_from_file_location("run_pipeline", run_pipeline_path)
        run_pipeline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_pipeline)
        run_pipeline.main()
    st.rerun()

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.title("🛡️ Fraud Risk Platform")
st.sidebar.markdown("---")

PAGES = {
    "Executive Overview":       "pages.page1_executive",
    "Fraud Watchlist":          "pages.page2_watchlist",
    "Cases & SLA":              "pages.page3_cases",
    "Fraud Patterns & Trends":  "pages.page4_patterns",
    "Monthly Fraud Review":     "pages.page5_review",
}

selection = st.sidebar.radio("Navigation", list(PAGES.keys()))
st.sidebar.markdown("---")
st.sidebar.caption("Fraud Detection & Risk Operations Platform")
st.sidebar.caption("Portfolio Project — Fresher Edition")

# ── Load selected page ────────────────────────────────────────────────────────
import importlib
module_path = PAGES[selection]
filepath    = os.path.join(
    PROJECT_ROOT, "dashboard",
    module_path.replace(".", os.sep) + ".py"
)
spec = importlib.util.spec_from_file_location(module_path, filepath)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.render()
