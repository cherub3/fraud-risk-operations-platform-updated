"""
Page 5: Monthly Fraud Review
Renders the management narrative documents alongside live KPI data.
"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.components.data_loader import load_kpis, load_audit_trail, load_cases

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR     = os.path.join(PROJECT_ROOT, "docs")


def load_doc(filename: str) -> str:
    path = os.path.join(DOCS_DIR, filename)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return f"*Document not found: {filename}*"


def render():
    st.title("Monthly Fraud Review")
    st.caption("Management reporting — what happened, why it happened, and what to do about it")

    kpis  = load_kpis()
    audit = load_audit_trail()
    cases = load_cases()

    # ── Live monthly metrics ──────────────────────────────────────────────────
    st.markdown("### This Month at a Glance")

    det  = kpis.get("detection", {})
    ops  = kpis.get("operations", {})
    risk = kpis.get("risk", {})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fraud Alert Rate",      f"{det.get('fraud_rate_pct',0)}%")
    c2.metric("SLA Compliance",        f"{ops.get('sla_compliance_pct',0)}%")
    c3.metric("Confirmed Fraud Value", f"${risk.get('fraud_amount_caught',0):,.0f}")
    c4.metric("Loss Exposure",         f"${risk.get('potential_loss_exposure',0):,.0f}")

    st.markdown("---")

    # ── Tabs for documents ────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "Executive Summary", "Key Findings", "Monthly Fraud Review"
    ])

    with tab1:
        st.markdown(load_doc("EXECUTIVE_SUMMARY.md"))

    with tab2:
        st.markdown(load_doc("KEY_FINDINGS.md"))

    with tab3:
        st.markdown(load_doc("MONTHLY_FRAUD_REVIEW.md"))

    st.markdown("---")

    # ── Resolution decision breakdown ─────────────────────────────────────────
    st.markdown("### Resolution Summary")
    if not audit.empty:
        resolutions = audit[audit["event_type"] == "Resolution"].copy()
        if not resolutions.empty:
            summary = resolutions.groupby("resolution_reason").agg(
                cases=("case_id", "count"),
                total_loss=("loss_amount", "sum"),
            ).reset_index()
            summary.columns = ["Decision", "Cases", "Total Loss ($)"]
            summary["Total Loss ($)"] = summary["Total Loss ($)"].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) else "—"
            )
            st.dataframe(summary, use_container_width=True)

    # ── Audit trail ───────────────────────────────────────────────────────────
    st.markdown("### Recent Audit Trail (Last 20 Events)")
    if not audit.empty:
        recent_audit = audit.sort_values("event_at", ascending=False).head(20)[[
            "event_at", "case_id", "event_type", "performed_by",
            "sla_compliant", "resolution_reason", "loss_amount"
        ]].copy()
        recent_audit["event_at"]     = recent_audit["event_at"].dt.strftime("%Y-%m-%d %H:%M")
        recent_audit["loss_amount"]  = recent_audit["loss_amount"].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) and x > 0 else "—"
        )
        recent_audit["sla_compliant"] = recent_audit["sla_compliant"].map(
            {True: "✅ Yes", False: "❌ No", None: "—"}
        )
        recent_audit.columns = [
            "Event Time", "Case ID", "Event Type", "Actor",
            "SLA Met", "Decision", "Loss Amount"
        ]
        st.dataframe(recent_audit, use_container_width=True)
