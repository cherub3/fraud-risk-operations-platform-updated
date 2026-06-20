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
# st.cache_resource is process-wide and Streamlit serialises concurrent calls to the
# same cached function internally, so this runs exactly once no matter how many
# sessions/reruns hit it at the same time — no manual locking or polling needed.
DB_PATH  = os.path.join(PROJECT_ROOT, "database", "fraud_platform.duckdb")
KPI_PATH = os.path.join(PROJECT_ROOT, "data", "outputs", "executive_kpis.json")


@st.cache_resource(show_spinner="First-time setup: building the fraud database (~15s)...")
def ensure_database_built() -> bool:
    if os.path.exists(DB_PATH) and os.path.exists(KPI_PATH):
        return True

    # Start from a guaranteed-clean file so foreign-key ordering in the
    # pipeline's per-table deletes can never conflict with leftover data
    # from a previous partial/crashed build.
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    wal_path = DB_PATH + ".wal"
    if os.path.exists(wal_path):
        os.remove(wal_path)

    import importlib.util

    run_pipeline_path = os.path.join(PROJECT_ROOT, "etl", "run_pipeline.py")
    spec = importlib.util.spec_from_file_location("run_pipeline", run_pipeline_path)
    run_pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_pipeline)
    run_pipeline.main()
    return True


ensure_database_built()

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.title("🛡️ Fraud Risk Platform")
st.sidebar.markdown("---")

PAGES = {
    "Executive Overview":       "views.page1_executive",
    "Fraud Watchlist":          "views.page2_watchlist",
    "Cases & SLA":              "views.page3_cases",
    "Fraud Patterns & Trends":  "views.page4_patterns",
    "Monthly Fraud Review":     "views.page5_review",
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
