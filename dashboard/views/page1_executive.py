"""
Page 1: Executive Overview
Top-level KPIs: fraud rate, loss exposure, open cases, SLA compliance, watchlist.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.components.data_loader import (
    load_kpis, load_fraud_scores, load_cases, load_audit_trail
)

TIER_COLORS = {
    "Critical": "#d62728",
    "High":     "#ff7f0e",
    "Medium":   "#ffbb78",
    "Low":      "#2ca02c",
}


def metric_card(label: str, value: str, delta: str = "", color: str = "#1f77b4"):
    st.markdown(f"""
    <div style="background:#1e2130;border-radius:8px;padding:16px 20px;border-left:4px solid {color};">
        <div style="color:#aaa;font-size:12px;text-transform:uppercase;letter-spacing:1px">{label}</div>
        <div style="color:#fff;font-size:28px;font-weight:700;margin-top:4px">{value}</div>
        <div style="color:#aaa;font-size:12px;margin-top:2px">{delta}</div>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.title("Executive Overview")
    st.caption("Real-time fraud operations dashboard")

    kpis   = load_kpis()
    scores = load_fraud_scores()
    cases  = load_cases()
    audit  = load_audit_trail()

    if not kpis:
        st.error("No KPI data found. Run the pipeline first: `python etl/run_pipeline.py`")
        return

    det = kpis.get("detection", {})
    ops = kpis.get("operations", {})
    risk = kpis.get("risk", {})
    wl   = kpis.get("watchlist", {})

    # ── Row 1: Detection KPIs ─────────────────────────────────────────────────
    st.markdown("### Detection")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Transactions",
                    f"{det.get('total_transactions',0):,}",
                    "Last 90 days", "#1f77b4")
    with c2:
        metric_card("Fraud Alerts",
                    f"{det.get('fraud_alerts',0):,}",
                    f"{det.get('fraud_rate_pct',0)}% alert rate", "#ff7f0e")
    with c3:
        metric_card("Confirmed Fraud Cases",
                    f"{det.get('confirmed_fraud_cases',0):,}",
                    "Investigated & confirmed", "#d62728")
    with c4:
        metric_card("False Positives",
                    f"{det.get('false_positives',0):,}",
                    f"${risk.get('false_positive_cost',0):,.0f} wasted investigation cost", "#9467bd")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Operations KPIs ────────────────────────────────────────────────
    st.markdown("### Operations")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Open Cases",
                    f"{ops.get('open_cases',0):,}",
                    "Awaiting assignment", "#2ca02c")
    with c2:
        metric_card("Escalated Cases",
                    f"{ops.get('escalated_cases',0):,}",
                    "Senior review required", "#d62728")
    with c3:
        metric_card("SLA Compliance",
                    f"{ops.get('sla_compliance_pct',0):.1f}%",
                    f"{ops.get('sla_breaches',0)} breaches", "#1f77b4")
    with c4:
        metric_card("Watchlist Active",
                    f"{wl.get('total_active',0):,}",
                    f"{wl.get('high_priority',0)} high priority", "#ff7f0e")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 3: Risk / Financial KPIs ──────────────────────────────────────────
    st.markdown("### Risk & Financial Impact")
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Fraud Amount Caught",
                    f"${risk.get('fraud_amount_caught',0):,.0f}",
                    "Confirmed fraud value", "#d62728")
    with c2:
        metric_card("Potential Loss Exposure",
                    f"${risk.get('potential_loss_exposure',0):,.0f}",
                    "Open + Investigating + Escalated cases", "#ff7f0e")
    with c3:
        metric_card("Loss Avoided",
                    f"${risk.get('loss_avoided',0):,.0f}",
                    "Estimated value saved by catching fraud", "#2ca02c")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Charts ────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Risk Tier Distribution")
        tier_data = kpis.get("tier_distribution", {})
        if tier_data:
            tiers  = list(tier_data.keys())
            counts = list(tier_data.values())
            colors = [TIER_COLORS.get(t, "#888") for t in tiers]
            fig = go.Figure(go.Bar(
                x=tiers, y=counts,
                marker_color=colors,
                text=counts, textposition="outside"
            ))
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc",
                showlegend=False,
                margin=dict(t=20, b=20),
                xaxis=dict(categoryorder="array",
                           categoryarray=["Critical", "High", "Medium", "Low"]),
                yaxis_title="Alert Count",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### Daily Fraud Alert Trend (30 days)")
        if not scores.empty:
            recent = scores[scores["fraud_label"] == "Fraud"].copy()
            recent["date"] = recent["transaction_date"].dt.date
            daily = recent.groupby("date").size().reset_index(name="alerts")
            daily = daily.tail(30)
            fig2 = px.line(daily, x="date", y="alerts",
                           color_discrete_sequence=["#ff7f0e"])
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc",
                margin=dict(t=20, b=20),
                xaxis_title="", yaxis_title="Fraud Alerts",
            )
            fig2.update_traces(fill="tozeroy", fillcolor="rgba(255,127,14,0.1)")
            st.plotly_chart(fig2, use_container_width=True)

    # ── Case status donut ─────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Case Status Breakdown")
        if not cases.empty:
            status_counts = cases["current_status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig3 = go.Figure(go.Pie(
                labels=status_counts["Status"],
                values=status_counts["Count"],
                hole=0.5,
                marker_colors=["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728"]
            ))
            fig3.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc",
                margin=dict(t=10, b=10),
                showlegend=True,
            )
            st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.markdown("#### Case Aging (Active Cases)")
        aging_data = kpis.get("aging_distribution", {})
        if aging_data:
            labels = list(aging_data.keys())
            vals   = list(aging_data.values())
            aging_colors = {
                "Fresh":          "#2ca02c",
                "Aging":          "#ff7f0e",
                "Critical Aging": "#d62728",
            }
            colors_list = [aging_colors.get(l, "#888") for l in labels]
            fig4 = go.Figure(go.Bar(
                x=labels, y=vals,
                marker_color=colors_list,
                text=vals, textposition="outside"
            ))
            fig4.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc",
                margin=dict(t=20, b=20),
                yaxis_title="Cases",
            )
            st.plotly_chart(fig4, use_container_width=True)
