"""
Page 2: Fraud Watchlist
Proactive early-warning system — accounts at rising risk before fraud is confirmed.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.components.data_loader import load_watchlist

PRIORITY_COLOR = {"High": "#d62728", "Medium": "#ff7f0e", "Low": "#2ca02c"}
TREND_ICON = {"Increasing": "↑", "Stable": "→", "Decreasing": "↓"}
TREND_COLOR = {"Increasing": "red", "Stable": "orange", "Decreasing": "green"}


def render():
    st.title("Fraud Watchlist")
    st.caption("Accounts showing rising fraud risk signals — early warning before confirmed fraud")

    wl = load_watchlist()

    if wl.empty:
        st.warning("No watchlist data. Run the pipeline first.")
        return

    # ── Summary metrics ───────────────────────────────────────────────────────
    total     = len(wl)
    active    = (wl["watchlist_status"] == "Active").sum()
    high_pri  = (wl["priority"] == "High").sum()
    increasing = (wl["risk_trend"] == "Increasing").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Watchlist Accounts", total)
    c2.metric("Active (Flagged)", active)
    c3.metric("High Priority", high_pri)
    c4.metric("Increasing Risk Trend", increasing)

    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        status_filter = st.multiselect(
            "Status", options=wl["watchlist_status"].unique().tolist(),
            default=wl["watchlist_status"].unique().tolist()
        )
    with col_f2:
        priority_filter = st.multiselect(
            "Priority", options=["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )
    with col_f3:
        trend_filter = st.multiselect(
            "Risk Trend", options=wl["risk_trend"].unique().tolist(),
            default=wl["risk_trend"].unique().tolist()
        )

    filtered = wl[
        wl["watchlist_status"].isin(status_filter) &
        wl["priority"].isin(priority_filter) &
        wl["risk_trend"].isin(trend_filter)
    ].copy()

    st.markdown(f"**Showing {len(filtered):,} accounts**")

    # ── Charts ────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Watchlist by Priority")
        pri_counts = filtered["priority"].value_counts().reset_index()
        pri_counts.columns = ["Priority", "Count"]
        pri_order = ["High", "Medium", "Low"]
        pri_counts["Priority"] = pd.Categorical(pri_counts["Priority"], categories=pri_order, ordered=True)
        pri_counts = pri_counts.sort_values("Priority")
        fig = go.Figure(go.Bar(
            x=pri_counts["Priority"],
            y=pri_counts["Count"],
            marker_color=[PRIORITY_COLOR.get(p, "#888") for p in pri_counts["Priority"]],
            text=pri_counts["Count"], textposition="outside"
        ))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10),
            yaxis_title="Accounts"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### Risk Trend Distribution")
        trend_counts = filtered["risk_trend"].value_counts().reset_index()
        trend_counts.columns = ["Trend", "Count"]
        fig2 = go.Figure(go.Pie(
            labels=trend_counts["Trend"],
            values=trend_counts["Count"],
            hole=0.5,
            marker_colors=["#d62728", "#ff7f0e", "#2ca02c"]
        ))
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Signal heatmap ────────────────────────────────────────────────────────
    st.markdown("#### Signal Breakdown — Alert, Score & Merchant Trends")
    signal_cols = ["alert_freq_trend", "score_trend", "merchant_div_trend"]
    signal_labels = ["Alert Frequency", "Fraud Score", "Merchant Diversity"]

    signal_df = filtered[signal_cols].copy()
    signal_df.columns = signal_labels
    signal_summary = signal_df.apply(pd.value_counts).fillna(0).T
    for col in ["Up", "Stable", "Down"]:
        if col not in signal_summary.columns:
            signal_summary[col] = 0

    fig3 = go.Figure(data=go.Heatmap(
        z=signal_summary[["Up", "Stable", "Down"]].values,
        x=["Up ↑", "Stable →", "Down ↓"],
        y=signal_summary.index.tolist(),
        colorscale=[[0, "#2ca02c"], [0.5, "#ffbb78"], [1, "#d62728"]],
        text=signal_summary[["Up", "Stable", "Down"]].values,
        texttemplate="%{text:.0f}",
        showscale=False,
    ))
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc", margin=dict(t=10, b=10), height=180,
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Watchlist table ───────────────────────────────────────────────────────
    st.markdown("#### Watchlist Accounts")

    display_cols = [
        "account_id", "watchlist_status", "priority", "risk_trend",
        "watchlist_reason", "recommended_action",
        "alert_count_30d", "avg_fraud_score_30d", "merchant_count_30d"
    ]
    display = filtered[display_cols].copy().sort_values(
        by=["priority", "risk_trend"],
        key=lambda col: col.map({"High": 0, "Medium": 1, "Low": 2, "Increasing": 0, "Stable": 1, "Decreasing": 2})
        if col.name in ("priority", "risk_trend") else col
    )
    display.columns = [
        "Account", "Status", "Priority", "Risk Trend",
        "Reason", "Recommended Action",
        "Alerts (30d)", "Avg Score (30d)", "Merchants (30d)"
    ]

    def highlight_priority(row):
        if row["Priority"] == "High":
            return ["background-color: rgba(214,39,40,0.15)"] * len(row)
        elif row["Priority"] == "Medium":
            return ["background-color: rgba(255,127,14,0.10)"] * len(row)
        return [""] * len(row)

    st.dataframe(
        display.style.apply(highlight_priority, axis=1),
        use_container_width=True,
        height=450,
    )

    # ── Recommended actions summary ───────────────────────────────────────────
    st.markdown("#### Recommended Actions Summary")
    action_summary = filtered["recommended_action"].value_counts().reset_index()
    action_summary.columns = ["Action", "Accounts"]
    for _, row in action_summary.iterrows():
        icon = "🔴" if "Block" in row["Action"] else "🟡" if "priority" in row["Action"].lower() else "🟢"
        st.markdown(f"{icon} **{row['Action']}** — {row['Accounts']} accounts")
