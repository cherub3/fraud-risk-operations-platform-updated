"""
Layer 7: Executive KPIs
Computes all KPIs and saves them to a JSON file for the dashboard.

Detection KPIs:   fraud alerts, confirmed fraud, fraud rate
Operations KPIs:  open cases, escalated cases, SLA compliance
Risk KPIs:        fraud amount caught, fraud missed, loss exposure,
                  false positive cost, loss avoided
"""

import pandas as pd
import duckdb
import json
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import get_connection

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "outputs", "executive_kpis.json"
)

# Assumptions for business impact calculations
AVG_INVESTIGATION_COST = 150   # $ per false positive investigation
LOSS_RECOVERY_RATE     = 0.35  # 35% of confirmed fraud losses are recovered


def run():
    con = get_connection()
    print("Computing executive KPIs...")

    # ── Detection KPIs ────────────────────────────────────────────────────────
    total_txns = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    fraud_alerts = con.execute(
        "SELECT COUNT(*) FROM fraud_scores WHERE fraud_label = 'Fraud'"
    ).fetchone()[0]

    confirmed_fraud = con.execute("""
        SELECT COUNT(DISTINCT case_id)
        FROM audit_trail
        WHERE event_type = 'Resolution'
          AND resolution_reason = 'Fraud Confirmed'
    """).fetchone()[0]

    false_positives = con.execute("""
        SELECT COUNT(DISTINCT case_id)
        FROM audit_trail
        WHERE event_type = 'Resolution'
          AND resolution_reason = 'False Positive'
    """).fetchone()[0]

    fraud_rate = round(fraud_alerts / total_txns * 100, 2) if total_txns > 0 else 0

    # ── Operations KPIs ───────────────────────────────────────────────────────
    case_statuses = con.execute("""
        SELECT current_status, COUNT(*) AS cnt
        FROM fraud_cases
        GROUP BY current_status
    """).df()
    status_dict = dict(zip(case_statuses["current_status"], case_statuses["cnt"]))

    open_cases       = status_dict.get("Open", 0)
    investigating    = status_dict.get("Investigating", 0)
    escalated_cases  = status_dict.get("Escalated", 0)
    resolved_cases   = status_dict.get("Resolved", 0)

    sla_data = con.execute("""
        SELECT
            COUNT(*) AS total_resolved,
            SUM(CASE WHEN sla_compliant THEN 1 ELSE 0 END) AS compliant
        FROM audit_trail
        WHERE event_type = 'Resolution'
    """).fetchone()
    total_resolved = sla_data[0] or 1
    sla_compliant_count = sla_data[1] or 0
    sla_compliance_pct = round(sla_compliant_count / total_resolved * 100, 1)

    sla_breaches = con.execute(
        "SELECT COUNT(*) FROM audit_trail WHERE event_type = 'SLA_Breach'"
    ).fetchone()[0]

    # ── Risk / Financial KPIs ─────────────────────────────────────────────────
    fraud_amount_caught = con.execute("""
        SELECT COALESCE(SUM(loss_amount), 0)
        FROM audit_trail
        WHERE event_type = 'Resolution'
          AND resolution_reason = 'Fraud Confirmed'
    """).fetchone()[0]

    # Missed fraud = true label fraud transactions that were NOT flagged
    missed_fraud = con.execute("""
        SELECT COALESCE(SUM(t.amount), 0)
        FROM transactions t
        LEFT JOIN fraud_scores fs ON t.transaction_id = fs.transaction_id
        WHERE t.true_label = 1
          AND (fs.fraud_label = 'Not Fraud' OR fs.fraud_label IS NULL)
    """).fetchone()[0]

    # Potential loss exposure = open + investigating + escalated cases
    exposure = con.execute("""
        SELECT COALESCE(SUM(case_amount), 0)
        FROM fraud_cases
        WHERE current_status IN ('Open', 'Investigating', 'Escalated')
    """).fetchone()[0]

    false_positive_cost = round(false_positives * AVG_INVESTIGATION_COST, 2)
    loss_avoided = round(float(fraud_amount_caught) * (1 - LOSS_RECOVERY_RATE), 2)

    # ── Watchlist KPIs ────────────────────────────────────────────────────────
    watchlist_total  = con.execute(
        "SELECT COUNT(*) FROM fraud_watchlist WHERE watchlist_status = 'Active'"
    ).fetchone()[0]
    watchlist_high   = con.execute(
        "SELECT COUNT(*) FROM fraud_watchlist WHERE priority = 'High'"
    ).fetchone()[0]

    # ── Tier breakdown ────────────────────────────────────────────────────────
    tier_dist = con.execute("""
        SELECT risk_tier, COUNT(*) AS cnt
        FROM fraud_scores
        GROUP BY risk_tier
    """).df()
    tier_dict = dict(zip(tier_dist["risk_tier"], tier_dist["cnt"]))

    # ── Aging breakdown ───────────────────────────────────────────────────────
    aging = con.execute("""
        SELECT aging_status, COUNT(*) AS cnt
        FROM fraud_cases
        WHERE current_status NOT IN ('Resolved')
        GROUP BY aging_status
    """).df()
    aging_dict = dict(zip(aging["aging_status"], aging["cnt"]))

    kpis = {
        "generated_at": datetime.now().isoformat(),
        "detection": {
            "total_transactions":   total_txns,
            "fraud_alerts":         fraud_alerts,
            "confirmed_fraud_cases": confirmed_fraud,
            "false_positives":      false_positives,
            "fraud_rate_pct":       fraud_rate,
        },
        "operations": {
            "open_cases":          open_cases,
            "investigating_cases": investigating,
            "escalated_cases":     escalated_cases,
            "resolved_cases":      resolved_cases,
            "sla_compliance_pct":  sla_compliance_pct,
            "sla_breaches":        sla_breaches,
        },
        "risk": {
            "fraud_amount_caught":   round(float(fraud_amount_caught), 2),
            "fraud_missed":          round(float(missed_fraud), 2),
            "potential_loss_exposure": round(float(exposure), 2),
            "false_positive_cost":   false_positive_cost,
            "loss_avoided":          loss_avoided,
        },
        "watchlist": {
            "total_active":   watchlist_total,
            "high_priority":  watchlist_high,
        },
        "tier_distribution": tier_dict,
        "aging_distribution": aging_dict,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(kpis, f, indent=2)

    print(f"  Fraud alerts:         {fraud_alerts:,}  ({fraud_rate}% of transactions)")
    print(f"  Confirmed fraud:      {confirmed_fraud:,}")
    print(f"  SLA compliance:       {sla_compliance_pct}%")
    print(f"  Loss exposure:        ${float(exposure):,.0f}")
    print(f"  Loss avoided:         ${loss_avoided:,.0f}")
    print(f"  Watchlist (active):   {watchlist_total:,}")
    print(f"\nSaved: {OUTPUT_PATH}")

    con.close()
    print("Layer 7 complete.\n")


if __name__ == "__main__":
    run()
