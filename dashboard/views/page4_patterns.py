"""
Page 4: Fraud Patterns & Trends
Fraud trend over time, alert volume, merchant analysis, risk tier distribution, hour-of-day heatmap.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.components.data_loader import load_fraud_scores, load_transactions

TIER_COLORS = {
    "Critical": "#d62728",
    "High":     "#ff7f0e",
    "Medium":   "#ffbb78",
    "Low":      "#2ca02c",
}

DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def render():
    st.title("Fraud Patterns & Trends")
    st.caption("Where, when, and how fraud is happening")

    scores = load_fraud_scores()
    txns   = load_transactions()

    if scores.empty:
        st.warning("No score data. Run the pipeline first.")
        return

    fraud_only = scores[scores["fraud_label"] == "Fraud"].copy()
    fraud_only["date"] = fraud_only["transaction_date"].dt.date
    fraud_only["week"] = fraud_only["transaction_date"].dt.to_period("W").astype(str)

    # ── Summary ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Fraud Alerts", f"{len(fraud_only):,}")
    c2.metric("Unique Accounts Flagged", f"{fraud_only['account_id'].nunique():,}")
    c3.metric("Avg Fraud Score", f"{fraud_only['fraud_score'].mean():.1f}")
    top_cat = fraud_only["merchant_category"].value_counts().index[0]
    c4.metric("Top Risk Merchant Category", top_cat)

    st.markdown("---")

    # ── Weekly fraud trend ────────────────────────────────────────────────────
    st.markdown("#### Weekly Fraud Alert Trend")
    weekly = fraud_only.groupby("week").agg(
        alerts=("transaction_id", "count"),
        avg_score=("fraud_score", "mean"),
        total_amount=("amount", "sum"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weekly["week"], y=weekly["alerts"],
        name="Fraud Alerts", marker_color="#ff7f0e", opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=weekly["week"], y=weekly["avg_score"],
        name="Avg Fraud Score", yaxis="y2",
        line=dict(color="#d62728", width=2)
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc", margin=dict(t=10, b=10),
        yaxis=dict(title="Alert Count"),
        yaxis2=dict(title="Avg Score", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1),
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)

    col_left, col_right = st.columns(2)

    # ── Merchant category breakdown ───────────────────────────────────────────
    with col_left:
        st.markdown("#### Fraud by Merchant Category")
        merch = fraud_only.groupby("merchant_category").agg(
            alerts=("transaction_id", "count"),
            total_amount=("amount", "sum"),
        ).reset_index().sort_values("alerts", ascending=True).tail(10)

        fig2 = go.Figure(go.Bar(
            y=merch["merchant_category"],
            x=merch["alerts"],
            orientation="h",
            marker_color="#ff7f0e",
            text=merch["alerts"], textposition="outside",
        ))
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10, l=10),
            xaxis_title="Alert Count",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Risk tier distribution ────────────────────────────────────────────────
    with col_right:
        st.markdown("#### Risk Tier Distribution")
        tier_df = scores.groupby("risk_tier").size().reset_index(name="count")
        tier_order = ["Critical", "High", "Medium", "Low"]
        tier_df["risk_tier"] = pd.Categorical(tier_df["risk_tier"], categories=tier_order, ordered=True)
        tier_df = tier_df.sort_values("risk_tier")
        fig3 = go.Figure(go.Bar(
            x=tier_df["risk_tier"],
            y=tier_df["count"],
            marker_color=[TIER_COLORS.get(t, "#888") for t in tier_df["risk_tier"]],
            text=tier_df["count"], textposition="outside"
        ))
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10),
            yaxis_title="Alert Count",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Hour-of-day heatmap ───────────────────────────────────────────────────
    st.markdown("#### Fraud Alert Heatmap — Hour of Day vs Day of Week")
    fraud_only["day_of_week"] = fraud_only["transaction_date"].dt.dayofweek
    heatmap_data = fraud_only.groupby(["day_of_week", "hour_of_day"]).size().reset_index(name="count")
    heatmap_pivot = heatmap_data.pivot(index="day_of_week", columns="hour_of_day", values="count").fillna(0)
    heatmap_pivot.index = [DAY_LABELS[i] for i in heatmap_pivot.index]

    fig4 = go.Figure(go.Heatmap(
        z=heatmap_pivot.values,
        x=[f"{h:02d}:00" for h in heatmap_pivot.columns],
        y=heatmap_pivot.index.tolist(),
        colorscale="YlOrRd",
        colorbar=dict(title="Alerts"),
    ))
    fig4.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc", margin=dict(t=10, b=10),
        xaxis_title="Hour of Day", yaxis_title="Day of Week",
        height=280,
    )
    st.plotly_chart(fig4, use_container_width=True)

    # ── Transaction type breakdown ────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Fraud by Transaction Type")
        type_df = fraud_only.groupby("transaction_type").agg(
            alerts=("transaction_id","count"),
            amount=("amount","sum")
        ).reset_index()
        fig5 = go.Figure(go.Pie(
            labels=type_df["transaction_type"],
            values=type_df["alerts"],
            hole=0.45,
            marker_colors=["#1f77b4","#ff7f0e","#d62728","#2ca02c"],
        ))
        fig5.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col_b:
        st.markdown("#### International vs Domestic Fraud")
        intl_df = fraud_only.groupby("is_international").agg(
            alerts=("transaction_id","count"),
            amount=("amount","sum")
        ).reset_index()
        intl_df["is_international"] = intl_df["is_international"].map({True: "International", False: "Domestic"})
        fig6 = go.Figure(go.Pie(
            labels=intl_df["is_international"],
            values=intl_df["alerts"],
            hole=0.45,
            marker_colors=["#d62728","#1f77b4"],
        ))
        fig6.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig6, use_container_width=True)

    # ── Fraud score distribution ───────────────────────────────────────────────
    st.markdown("#### Fraud Score Distribution")
    fig7 = px.histogram(
        fraud_only, x="fraud_score", nbins=30,
        color_discrete_sequence=["#ff7f0e"],
        labels={"fraud_score": "Fraud Score", "count": "Alerts"},
    )
    fig7.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc", margin=dict(t=10, b=10),
        yaxis_title="Number of Alerts",
    )
    st.plotly_chart(fig7, use_container_width=True)
