"""
Layer 4: Investigation Workflow
Builds the investigation log — status transitions and final decisions for each case.

For every case, this layer simulates the lifecycle:
  Open → Investigating → [Escalated] → Resolved

Each status change is logged with timestamp, actor, and decision.
Resolved cases carry a final decision: Fraud / False Positive / Inconclusive.
"""

import pandas as pd
import duckdb
import uuid
from datetime import datetime, timedelta
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import get_connection

random.seed(42)

RESOLUTION_DECISIONS = {
    "Critical": {"Fraud Confirmed": 0.62, "False Positive": 0.22, "Inconclusive": 0.16},
    "High":     {"Fraud Confirmed": 0.44, "False Positive": 0.36, "Inconclusive": 0.20},
}

ESCALATION_REASONS = [
    "High loss exposure — manager approval required",
    "Account shows prior fraud history",
    "Cross-border transaction pattern",
    "Multiple linked accounts flagged",
    "Organised fraud ring suspected",
]

RESOLUTION_NOTES = {
    "Fraud Confirmed":  "Transaction confirmed as fraudulent. Account blocked and loss reported.",
    "False Positive":   "Transaction verified as legitimate. Customer contacted and confirmed.",
    "Inconclusive":     "Insufficient evidence to confirm fraud. Monitoring continued.",
}


def build_log_entries(case: pd.Series) -> list:
    entries = []
    case_id    = case["case_id"]
    investigator = case["assigned_investigator"]
    tier       = case["risk_tier"]
    status     = case["current_status"]

    assigned_at = pd.to_datetime(case["assigned_at"])
    t = assigned_at

    def new_entry(from_s, to_s, at, decision=None, notes=None):
        return {
            "log_id":      f"LOG-{uuid.uuid4().hex[:10].upper()}",
            "case_id":     case_id,
            "status_from": from_s,
            "status_to":   to_s,
            "changed_at":  at.isoformat(),
            "changed_by":  investigator,
            "decision":    decision,
            "notes":       notes,
        }

    # Every case starts Open
    entries.append(new_entry("Created", "Open", t))

    if status == "Open":
        return entries

    # Open → Investigating
    t += timedelta(hours=random.uniform(0.5, 4))
    entries.append(new_entry("Open", "Investigating", t))

    if status == "Investigating":
        return entries

    if status == "Escalated":
        t += timedelta(hours=random.uniform(1, 8))
        reason = random.choice(ESCALATION_REASONS)
        entries.append(new_entry("Investigating", "Escalated", t, notes=reason))
        return entries

    # Resolved path
    if tier == "Critical" and random.random() < 0.25:
        # Some critical cases go through escalation before resolution
        t += timedelta(hours=random.uniform(1, 6))
        reason = random.choice(ESCALATION_REASONS)
        entries.append(new_entry("Investigating", "Escalated", t, notes=reason))
        t += timedelta(hours=random.uniform(2, 12))
        dist = RESOLUTION_DECISIONS[tier]
        decision = random.choices(list(dist.keys()), weights=list(dist.values()))[0]
        entries.append(new_entry("Escalated", "Resolved", t,
                                 decision=decision,
                                 notes=RESOLUTION_NOTES[decision]))
    else:
        t += timedelta(hours=random.uniform(2, 20))
        dist = RESOLUTION_DECISIONS[tier]
        decision = random.choices(list(dist.keys()), weights=list(dist.values()))[0]
        entries.append(new_entry("Investigating", "Resolved", t,
                                 decision=decision,
                                 notes=RESOLUTION_NOTES[decision]))

    return entries


def run():
    con = get_connection()

    print("Loading cases for investigation logging...")
    cases = con.execute("SELECT * FROM fraud_cases").df()
    print(f"  {len(cases):,} cases loaded.")

    all_logs = []
    for _, case in cases.iterrows():
        all_logs.extend(build_log_entries(case))

    log_df = pd.DataFrame(all_logs)

    con.execute("DELETE FROM investigation_log")
    con.register("log_stage", log_df)
    con.execute("INSERT INTO investigation_log SELECT * FROM log_stage")

    print(f"  Log entries created: {len(log_df):,}")
    resolved = log_df[log_df["decision"].notna()]
    print("  Decision breakdown:")
    for d, cnt in resolved["decision"].value_counts().items():
        print(f"    {d:20s}: {cnt:,}")

    con.close()
    print("Layer 4 complete.\n")


if __name__ == "__main__":
    run()
