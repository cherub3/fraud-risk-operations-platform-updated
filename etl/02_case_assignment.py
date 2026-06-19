"""
Layer 3: Case Assignment
Generates fraud cases for High and Critical tier alerts.
Assigns investigators, sets priorities, calculates SLA deadlines.

Business logic:
- Only High and Critical tier alerts generate cases (Medium/Low are logged, not cased)
- Priority maps to SLA deadline: P1=4h, P2=24h, P3=72h
- Investigators assigned round-robin within priority tier
- Case aging computed relative to assignment time
"""

import pandas as pd
import duckdb
import uuid
from datetime import datetime, timedelta
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import get_connection

INVESTIGATORS = [
    "Sarah Chen", "Marcus Johnson", "Priya Patel",
    "Tom Walsh", "Aisha Okafor", "David Kim"
]

# SLA hours by priority
SLA_HOURS = {"P1": 4, "P2": 24, "P3": 72}

# Priority assignment by risk tier
TIER_PRIORITY = {"Critical": "P1", "High": "P2"}

# Case statuses and their weights (to simulate a realistic in-progress queue)
STATUS_DISTRIBUTION = {
    "Critical": {"Resolved": 0.55, "Escalated": 0.15, "Investigating": 0.20, "Open": 0.10},
    "High":     {"Resolved": 0.60, "Escalated": 0.08, "Investigating": 0.22, "Open": 0.10},
}

RESOLUTION_DECISIONS = {
    "Critical": {"Fraud": 0.65, "False Positive": 0.20, "Inconclusive": 0.15},
    "High":     {"Fraud": 0.45, "False Positive": 0.35, "Inconclusive": 0.20},
}

random.seed(42)


def aging_status(assigned_at: datetime, now: datetime) -> str:
    hours_open = (now - assigned_at).total_seconds() / 3600
    if hours_open < 6:
        return "Fresh"
    elif hours_open < 24:
        return "Aging"
    else:
        return "Critical Aging"


def run():
    con = get_connection()
    now = datetime.now()

    print("Loading High and Critical fraud alerts...")
    alerts = con.execute("""
        SELECT
            fs.transaction_id,
            fs.fraud_score,
            fs.risk_tier,
            t.account_id,
            t.amount,
            t.transaction_date
        FROM fraud_scores fs
        JOIN transactions t ON fs.transaction_id = t.transaction_id
        WHERE fs.risk_tier IN ('High', 'Critical')
        ORDER BY fs.fraud_score DESC
    """).df()

    print(f"  {len(alerts):,} alerts eligible for case creation.")

    cases = []
    inv_index = {"P1": 0, "P2": 0, "P3": 0}  # round-robin counters

    for _, row in alerts.iterrows():
        tier     = row["risk_tier"]
        priority = TIER_PRIORITY[tier]

        # Round-robin investigator assignment
        inv = INVESTIGATORS[inv_index[priority] % len(INVESTIGATORS)]
        inv_index[priority] += 1

        # Simulate case assigned_at: sometime after the transaction, within last 90 days
        txn_time = pd.to_datetime(row["transaction_date"])
        delay_hours = random.randint(0, 6)
        assigned_at = txn_time + timedelta(hours=delay_hours)
        if assigned_at > now:
            assigned_at = now - timedelta(hours=random.randint(1, 48))

        sla_deadline = assigned_at + timedelta(hours=SLA_HOURS[priority])

        # Determine current status based on time elapsed and distribution
        dist = STATUS_DISTRIBUTION[tier]
        status = random.choices(list(dist.keys()), weights=list(dist.values()))[0]

        cases.append({
            "case_id":              f"CASE-{uuid.uuid4().hex[:10].upper()}",
            "transaction_id":       row["transaction_id"],
            "account_id":           row["account_id"],
            "fraud_score":          row["fraud_score"],
            "risk_tier":            tier,
            "assigned_investigator": inv,
            "priority":             priority,
            "assigned_at":          assigned_at.isoformat(),
            "sla_deadline":         sla_deadline.isoformat(),
            "current_status":       status,
            "case_amount":          row["amount"],
            "aging_status":         aging_status(assigned_at, now),
        })

    cases_df = pd.DataFrame(cases)

    con.execute("DELETE FROM fraud_cases")
    con.register("cases_stage", cases_df)
    con.execute("INSERT INTO fraud_cases SELECT * FROM cases_stage")

    print(f"  Cases created: {len(cases_df):,}")
    print("  Status distribution:")
    for s, cnt in cases_df["current_status"].value_counts().items():
        print(f"    {s:14s}: {cnt:,}")
    print("  Aging distribution:")
    for a, cnt in cases_df["aging_status"].value_counts().items():
        print(f"    {a:16s}: {cnt:,}")

    con.close()
    print("Layer 3 complete.\n")


if __name__ == "__main__":
    run()
