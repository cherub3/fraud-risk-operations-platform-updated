"""
Page 3: Cases & SLA
Case status breakdown, aging, escalations, SLA breaches, investigator workload.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.components.data_loader import load_cases, load_audit_trail, load_investigation_log

STATUS_COLOR = {
    "Open":          "#1f77b4",
    "Investigating": "#ff7f0e",
    "Escalated":     "#d62728",
    "Resolved":      "#2ca02c",
}
AGING_COLOR = {
    "Fresh":          "#2ca02c",
    "Aging":          "#ff7f0e",
    "Critical Aging": "#d62728",
}


def render():
    st.title("Cases & SLA")
    st.caption("Case lifecycle management, SLA compliance, and investigator workload")

    cases = load_cases()
    audit = load_audit_trail()
    logs  = load_investigation_log()

    if cases.empty:
        st.warning("No case data. Run the pipeline first.")
        return

    now = pd.Timestamp.now()

    # ── Summary KPIs ──────────────────────────────────────────────────────────
    total_cases   = len(cases)
    open_cases    = (cases["current_status"] == "Open").sum()
    escalated     = (cases["current_status"] == "Escalated").sum()
    resolved      = (cases["current_status"] == "Resolved").sum()

    resolutions = audit[audit["event_type"] == "Resolution"]
    sla_ok   = resolutions["sla_compliant"].sum() if not resolutions.empty else 0
    sla_tot  = len(resolutions)
    sla_pct  = round(sla_ok / sla_tot * 100, 1) if sla_tot > 0 else 0
    sla_breaches = (audit["event_type"] == "SLA_Breach").sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Cases",    f"{total_cases:,}")
    c2.metric("Open",           f"{open_cases:,}")
    c3.metric("Escalated",      f"{escalated:,}", delta=f"{escalated} need review", delta_color="inverse")
    c4.metric("SLA Compliance", f"{sla_pct}%")
    c5.metric("SLA Breaches",   f"{sla_breaches:,}", delta_color="inverse")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # ── Case status bar ───────────────────────────────────────────────────────
    with col_left:
        st.markdown("#### Case Status")
        status_counts = cases["current_status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = go.Figure(go.Bar(
            x=status_counts["Status"],
            y=status_counts["Count"],
            marker_color=[STATUS_COLOR.get(s, "#888") for s in status_counts["Status"]],
            text=status_counts["Count"], textposition="outside"
        ))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10), yaxis_title="Cases"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Aging breakdown ───────────────────────────────────────────────────────
    with col_right:
        st.markdown("#### Case Aging (Active Cases)")
        active = cases[cases["current_status"] != "Resolved"].copy()
        if not active.empty:
            aging_counts = active["aging_status"].value_counts().reset_index()
            aging_counts.columns = ["Aging", "Count"]
            fig2 = go.Figure(go.Bar(
                x=aging_counts["Aging"],
                y=aging_counts["Count"],
                marker_color=[AGING_COLOR.get(a, "#888") for a in aging_counts["Aging"]],
                text=aging_counts["Count"], textposition="outside"
            ))
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc", margin=dict(t=10, b=10), yaxis_title="Cases"
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── Investigator workload ─────────────────────────────────────────────────
    st.markdown("#### Investigator Workload")
    active_cases = cases[cases["current_status"].isin(["Open", "Investigating", "Escalated"])]
    if not active_cases.empty:
        inv_load = active_cases.groupby(["assigned_investigator", "current_status"]).size().reset_index(name="count")
        fig3 = px.bar(
            inv_load, x="assigned_investigator", y="count", color="current_status",
            color_discrete_map=STATUS_COLOR,
            labels={"assigned_investigator": "Investigator", "count": "Active Cases", "current_status": "Status"},
            barmode="stack",
        )
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10),
            legend_title="Status",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── SLA breach timeline ───────────────────────────────────────────────────
    st.markdown("#### SLA Breach Timeline")
    breaches = audit[audit["event_type"] == "SLA_Breach"].copy()
    if not breaches.empty:
        breaches["date"] = breaches["event_at"].dt.date
        breach_daily = breaches.groupby("date").size().reset_index(name="breaches")
        fig4 = px.bar(breach_daily, x="date", y="breaches",
                      color_discrete_sequence=["#d62728"],
                      labels={"date": "Date", "breaches": "SLA Breaches"})
        fig4.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No SLA breaches recorded.")

    # ── Case table ────────────────────────────────────────────────────────────
    st.markdown("#### Active Case Queue")

    active_queue = cases[cases["current_status"] != "Resolved"].copy()
    active_queue = active_queue.sort_values(
        by=["priority", "fraud_score"], ascending=[True, False]
    )

    display = active_queue[[
        "case_id", "account_id", "risk_tier", "priority",
        "current_status", "aging_status", "assigned_investigator",
        "fraud_score", "case_amount", "sla_deadline"
    ]].copy()
    display["sla_deadline"] = display["sla_deadline"].dt.strftime("%Y-%m-%d %H:%M")
    display["fraud_score"]  = display["fraud_score"].round(1)
    display["case_amount"]  = display["case_amount"].apply(lambda x: f"${x:,.2f}")
    display.columns = [
        "Case ID", "Account", "Tier", "Priority", "Status", "Aging",
        "Investigator", "Score", "Amount", "SLA Deadline"
    ]

    def highlight_status(row):
        if row["Status"] == "Escalated":
            return ["background-color: rgba(214,39,40,0.15)"] * len(row)
        elif row["Aging"] == "Critical Aging":
            return ["background-color: rgba(255,127,14,0.15)"] * len(row)
        return [""] * len(row)

    st.dataframe(
        display.style.apply(highlight_status, axis=1),
        use_container_width=True,
        height=400,
    )

    # ── Decision outcomes ─────────────────────────────────────────────────────
    st.markdown("#### Resolution Decisions")
    decisions = logs[logs["decision"].notna()].copy()
    if not decisions.empty:
        dec_counts = decisions["decision"].value_counts().reset_index()
        dec_counts.columns = ["Decision", "Count"]
        fig5 = go.Figure(go.Pie(
            labels=dec_counts["Decision"],
            values=dec_counts["Count"],
            hole=0.5,
            marker_colors=["#d62728", "#2ca02c", "#ff7f0e"]
        ))
        fig5.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig5, use_container_width=True)
