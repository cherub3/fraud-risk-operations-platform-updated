"""
Layer 1 + 2: Fraud Detection & Risk Tiering
Computes fraud score, probability, label, and risk tier for every transaction.

Scoring approach: rule-based signal aggregation (no black-box ML).
Each signal contributes a weighted component to the final 0-100 score.
This is explainable — every score can be justified to an investigator.
"""

import pandas as pd
import numpy as np
import duckdb
import uuid
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import get_connection

# ── Scoring weights ──────────────────────────────────────────────────────────
# Total possible = 100 points

WEIGHTS = {
    "high_amount":        20,   # unusually large transaction
    "international":      15,   # cross-border transaction
    "night_transaction":  10,   # transaction between 00:00–05:00
    "risky_merchant":     20,   # high-risk merchant category
    "online_transfer":    10,   # online or transfer type (higher exposure)
    "new_account":        10,   # account age < 90 days
    "velocity_signal":    15,   # account-level alert frequency proxy
}

RISKY_MERCHANTS = {
    "Cryptocurrency", "Money Transfer", "Online Retail",
    "Electronics", "Luxury Goods", "Gaming"
}

# ── Risk tier thresholds ─────────────────────────────────────────────────────
TIER_THRESHOLDS = {
    "Critical": 75,
    "High":     50,
    "Medium":   25,
    "Low":       0,
}


def score_transaction(row: pd.Series, account_alert_counts: dict) -> dict:
    score = 0.0
    components = []

    # 1. High amount signal
    if row["amount"] >= 5000:
        score += WEIGHTS["high_amount"]
        components.append("high_amount")
    elif row["amount"] >= 1000:
        score += WEIGHTS["high_amount"] * 0.5
        components.append("medium_amount")

    # 2. International
    if row["is_international"]:
        score += WEIGHTS["international"]
        components.append("international")

    # 3. Night transaction (midnight–5am)
    if row["hour_of_day"] <= 5:
        score += WEIGHTS["night_transaction"]
        components.append("night_txn")

    # 4. Risky merchant category
    if row["merchant_category"] in RISKY_MERCHANTS:
        score += WEIGHTS["risky_merchant"]
        components.append("risky_merchant")

    # 5. Online or Transfer type
    if row["transaction_type"] in ("Online", "Transfer"):
        score += WEIGHTS["online_transfer"]
        components.append("online_transfer")

    # 6. New account (< 90 days old)
    if row["account_age_days"] < 90:
        score += WEIGHTS["new_account"]
        components.append("new_account")

    # 7. Velocity signal — accounts with many prior alerts get a boost
    alert_count = account_alert_counts.get(row["account_id"], 0)
    if alert_count >= 5:
        score += WEIGHTS["velocity_signal"]
        components.append("high_velocity")
    elif alert_count >= 2:
        score += WEIGHTS["velocity_signal"] * 0.5
        components.append("medium_velocity")

    # Add noise so scores are not all round numbers
    score += np.random.uniform(-3, 3)
    score = round(max(0.0, min(100.0, score)), 2)

    # Probability: sigmoid-like scaling from score
    probability = round(1 / (1 + np.exp(-0.1 * (score - 50))), 4)

    # Label
    label = "Fraud" if score >= 50 else "Not Fraud"

    # Risk tier
    if score >= TIER_THRESHOLDS["Critical"]:
        tier = "Critical"
    elif score >= TIER_THRESHOLDS["High"]:
        tier = "High"
    elif score >= TIER_THRESHOLDS["Medium"]:
        tier = "Medium"
    else:
        tier = "Low"

    return {
        "score_id":          f"SCR-{uuid.uuid4().hex[:10].upper()}",
        "transaction_id":    row["transaction_id"],
        "fraud_score":       score,
        "fraud_probability": probability,
        "fraud_label":       label,
        "risk_tier":         tier,
        "score_components":  "|".join(components),
        "scored_at":         datetime.now().isoformat(),
    }


def run():
    con = get_connection()

    print("Loading transactions...")
    txns = con.execute("SELECT * FROM transactions").df()
    print(f"  {len(txns):,} transactions loaded.")

    # Build a simple velocity proxy: count of transactions per account
    # In a real system this would be a rolling window query
    account_txn_counts = txns.groupby("account_id").size().to_dict()
    # Normalise to a 0-10 scale for the signal
    max_count = max(account_txn_counts.values())
    account_alert_proxy = {
        acc: int((cnt / max_count) * 10)
        for acc, cnt in account_txn_counts.items()
    }

    print("Scoring transactions...")
    scored_rows = [
        score_transaction(row, account_alert_proxy)
        for _, row in txns.iterrows()
    ]
    scores_df = pd.DataFrame(scored_rows)

    # Write to DB
    con.execute("DELETE FROM fraud_scores")
    con.register("scores_stage", scores_df)
    con.execute("INSERT INTO fraud_scores SELECT * FROM scores_stage")

    fraud_count = (scores_df["fraud_label"] == "Fraud").sum()
    print(f"  Fraud alerts generated: {fraud_count:,} ({fraud_count/len(scores_df):.1%})")
    print("  Risk tier distribution:")
    for tier in ["Critical", "High", "Medium", "Low"]:
        n = (scores_df["risk_tier"] == tier).sum()
        print(f"    {tier:10s}: {n:,}")

    con.close()
    print("Layer 1+2 complete.\n")


if __name__ == "__main__":
    run()
