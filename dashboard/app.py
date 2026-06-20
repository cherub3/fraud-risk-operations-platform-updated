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
# Concurrency-safe: Streamlit reruns this script on every page click, so multiple
# sessions can hit this block at nearly the same time. A lock file ensures only
# one of them actually rebuilds the database; the others wait for it to finish.
import time

DB_PATH   = os.path.join(PROJECT_ROOT, "database", "fraud_platform.duckdb")
KPI_PATH  = os.path.join(PROJECT_ROOT, "data", "outputs", "executive_kpis.json")
LOCK_PATH = os.path.join(PROJECT_ROOT, "database", ".pipeline_lock")
LOCK_STALE_SECONDS = 120  # if a lock is older than this, assume the builder crashed

def _lock_is_stale() -> bool:
    try:
        return (time.time() - os.path.getmtime(LOCK_PATH)) > LOCK_STALE_SECONDS
    except OSError:
        return True

def _try_acquire_lock() -> bool:
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        if _lock_is_stale():
            try:
                os.remove(LOCK_PATH)
            except OSError:
                pass
            return _try_acquire_lock()
        return False

def _release_lock():
    try:
        os.remove(LOCK_PATH)
    except OSError:
        pass

if not os.path.exists(DB_PATH) or not os.path.exists(KPI_PATH):
    if _try_acquire_lock():
        with st.spinner("First-time setup: building the fraud database (~15s)..."):
            try:
                # Start from a guaranteed-clean file so foreign-key ordering
                # in the pipeline's per-table deletes can never conflict with
                # leftover data from a previous partial/crashed build.
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
            finally:
                _release_lock()
        st.rerun()
    else:
        with st.spinner("Another session is building the database — waiting..."):
            for _ in range(60):  # wait up to ~60s
                time.sleep(1)
                if os.path.exists(DB_PATH) and os.path.exists(KPI_PATH):
                    break
        st.rerun()

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
