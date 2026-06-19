"""
Layer 5: Fraud Watchlist — Proactive Early Warning System

Identifies accounts showing increasing fraud risk BEFORE confirmed fraud.

Three trend signals per account (last 30 days vs prior 30 days):
  1. Alert Frequency Trend  — is the account generating more fraud alerts?
  2. Fraud Score Trend      — is the average fraud score rising?
  3. Merchant Diversity Trend — is the account transacting at more unique merchants?

Accounts are placed on the watchlist when ≥2 signals are trending Up.
This mirrors the early-warning logic used in credit risk monitoring.
"""

import pandas as pd
import numpy as np
import duckdb
import uuid
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import get_connection

NOW = datetime.now()
WINDOW_RECENT = 30   # days
WINDOW_PRIOR  = 30   # days prior to recent window

RECOMMENDED_ACTIONS = {
    ("Increasing", "High"):   "Block account pending review",
    ("Increasing", "Medium"): "Flag for priority investigation",
    ("Stable",     "High"):   "Enhanced monitoring — review weekly",
    ("Stable",     "Medium"): "Standard monitoring",
    ("Decreasing", "High"):   "Continue monitoring — risk reducing",
    ("Decreasing", "Medium"): "Routine review",
    ("Decreasing", "Low"):    "No action required",
    ("Stable",     "Low"):    "No action required",
    ("Increasing", "Low"):    "Flag for monitoring",
}


def compute_trend(recent_val: float, prior_val: float, threshold_pct: float = 0.15) -> str:
    if prior_val == 0:
        return "Up" if recent_val > 0 else "Stable"
    change = (recent_val - prior_val) / prior_val
    if change > threshold_pct:
        return "Up"
    elif change < -threshold_pct:
        return "Down"
    return "Stable"


def watchlist_reason(alert_trend: str, score_trend: str, merch_trend: str) -> str:
    reasons = []
    if alert_trend == "Up":
        reasons.append("alert frequency rising")
    if score_trend == "Up":
        reasons.append("fraud score escalating")
    if merch_trend == "Up":
        reasons.append("unusual merchant diversity")
    if not reasons:
        reasons.append("general risk elevation")
    return "; ".join(reasons).capitalize()


def run():
    con = get_connection()

    cutoff_recent = NOW - timedelta(days=WINDOW_RECENT)
    cutoff_prior  = NOW - timedelta(days=WINDOW_RECENT + WINDOW_PRIOR)

    print("Computing account-level trend signals...")

    # Recent window: last 30 days
    recent = con.execute(f"""
        SELECT
            t.account_id,
            COUNT(fs.score_id)              AS alert_count,
            AVG(fs.fraud_score)             AS avg_score,
            COUNT(DISTINCT t.merchant_id)   AS merchant_count
        FROM fraud_scores fs
        JOIN transactions t ON fs.transaction_id = t.transaction_id
        WHERE fs.fraud_label = 'Fraud'
          AND t.transaction_date >= '{cutoff_recent.isoformat()}'
        GROUP BY t.account_id
    """).df()

    # Prior window: 30–60 days ago
    prior = con.execute(f"""
        SELECT
            t.account_id,
            COUNT(fs.score_id)              AS alert_count,
            AVG(fs.fraud_score)             AS avg_score,
            COUNT(DISTINCT t.merchant_id)   AS merchant_count
        FROM fraud_scores fs
        JOIN transactions t ON fs.transaction_id = t.transaction_id
        WHERE fs.fraud_label = 'Fraud'
          AND t.transaction_date >= '{cutoff_prior.isoformat()}'
          AND t.transaction_date <  '{cutoff_recent.isoformat()}'
        GROUP BY t.account_id
    """).df()

    # Accounts with any recent activity
    all_accounts = con.execute(f"""
        SELECT DISTINCT account_id
        FROM transactions
        WHERE transaction_date >= '{cutoff_prior.isoformat()}'
    """).df()

    # Merge — fill missing with 0
    df = all_accounts.merge(
        recent.rename(columns={"alert_count": "r_alerts", "avg_score": "r_score", "merchant_count": "r_merch"}),
        on="account_id", how="left"
    ).merge(
        prior.rename(columns={"alert_count": "p_alerts", "avg_score": "p_score", "merchant_count": "p_merch"}),
        on="account_id", how="left"
    ).fillna(0)

    watchlist_rows = []
    for _, row in df.iterrows():
        alert_trend = compute_trend(row["r_alerts"], row["p_alerts"])
        score_trend = compute_trend(row["r_score"],  row["p_score"])
        merch_trend = compute_trend(row["r_merch"],  row["p_merch"])

        up_signals = sum(1 for t in [alert_trend, score_trend, merch_trend] if t == "Up")

        # Only watchlist accounts with ≥2 increasing signals
        if up_signals < 2:
            continue

        # Risk trend label
        if up_signals == 3:
            risk_trend = "Increasing"
            priority   = "High"
            status     = "Active"
        elif up_signals == 2:
            risk_trend = "Increasing"
            priority   = "Medium"
            status     = "Active"
        else:
            risk_trend = "Stable"
            priority   = "Low"
            status     = "Monitoring"

        reason = watchlist_reason(alert_trend, score_trend, merch_trend)
        action = RECOMMENDED_ACTIONS.get(
            (risk_trend, priority),
            "Flag for monitoring"
        )

        watchlist_rows.append({
            "watchlist_id":       f"WL-{uuid.uuid4().hex[:10].upper()}",
            "account_id":         row["account_id"],
            "watchlist_status":   status,
            "risk_trend":         risk_trend,
            "alert_freq_trend":   alert_trend,
            "score_trend":        score_trend,
            "merchant_div_trend": merch_trend,
            "watchlist_reason":   reason,
            "recommended_action": action,
            "priority":           priority,
            "added_at":           NOW.isoformat(),
            "last_reviewed":      NOW.isoformat(),
            "alert_count_30d":    int(row["r_alerts"]),
            "avg_fraud_score_30d": round(float(row["r_score"]), 2),
            "merchant_count_30d": int(row["r_merch"]),
        })

    wl_df = pd.DataFrame(watchlist_rows)

    con.execute("DELETE FROM fraud_watchlist")
    if len(wl_df) > 0:
        con.register("wl_stage", wl_df)
        con.execute("INSERT INTO fraud_watchlist SELECT * FROM wl_stage")

    print(f"  Accounts on watchlist: {len(wl_df):,}")
    if len(wl_df) > 0:
        print("  Priority breakdown:")
        for p, cnt in wl_df["priority"].value_counts().items():
            print(f"    {p:8s}: {cnt:,}")

    con.close()
    print("Layer 5 complete.\n")


if __name__ == "__main__":
    run()
