"""
Layer 6: Escalation, Resolution & Audit Trail

Builds the audit trail from investigation log data:
  - Records every escalation with reason
  - Records every resolution with decision and loss amount
  - Computes SLA compliance for each resolved case
  - Flags SLA breaches

SLA compliance = case resolved before sla_deadline.
"""

import pandas as pd
import duckdb
import uuid
from datetime import datetime
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import get_connection

random.seed(42)

ESCALATION_REASONS = [
    "High loss exposure — manager approval required",
    "Account shows prior fraud history",
    "Cross-border transaction pattern",
    "Multiple linked accounts flagged",
    "Organised fraud ring suspected",
]

LOSS_RATE_BY_DECISION = {
    "Fraud Confirmed":  0.90,   # 90% of confirmed fraud results in a loss
    "False Positive":   0.00,
    "Inconclusive":     0.20,
}


def run():
    con = get_connection()

    print("Building audit trail...")

    cases = con.execute("SELECT * FROM fraud_cases").df()
    logs  = con.execute("SELECT * FROM investigation_log").df()

    # Parse timestamps
    cases["assigned_at"]   = pd.to_datetime(cases["assigned_at"])
    cases["sla_deadline"]  = pd.to_datetime(cases["sla_deadline"])
    logs["changed_at"]     = pd.to_datetime(logs["changed_at"])

    audit_rows = []

    for _, case in cases.iterrows():
        case_id    = case["case_id"]
        case_logs  = logs[logs["case_id"] == case_id].sort_values("changed_at")

        # ── Assignment event ──────────────────────────────────────────────
        audit_rows.append({
            "audit_id":          f"AUD-{uuid.uuid4().hex[:10].upper()}",
            "case_id":           case_id,
            "event_type":        "Assignment",
            "event_at":          case["assigned_at"].isoformat(),
            "performed_by":      case["assigned_investigator"],
            "sla_compliant":     None,
            "resolution_reason": None,
            "escalation_reason": None,
            "loss_amount":       None,
            "notes":             f"Case assigned. SLA deadline: {case['sla_deadline'].date()}",
        })

        for _, log in case_logs.iterrows():
            # ── Escalation events ─────────────────────────────────────────
            if log["status_to"] == "Escalated":
                audit_rows.append({
                    "audit_id":          f"AUD-{uuid.uuid4().hex[:10].upper()}",
                    "case_id":           case_id,
                    "event_type":        "Escalation",
                    "event_at":          log["changed_at"].isoformat(),
                    "performed_by":      log["changed_by"],
                    "sla_compliant":     None,
                    "resolution_reason": None,
                    "escalation_reason": log["notes"] or random.choice(ESCALATION_REASONS),
                    "loss_amount":       None,
                    "notes":             "Case escalated for senior review.",
                })

            # ── Resolution events ─────────────────────────────────────────
            if log["status_to"] == "Resolved" and log["decision"]:
                resolved_at  = log["changed_at"]
                sla_compliant = resolved_at <= case["sla_deadline"]

                # SLA breach audit entry if breached
                if not sla_compliant:
                    audit_rows.append({
                        "audit_id":          f"AUD-{uuid.uuid4().hex[:10].upper()}",
                        "case_id":           case_id,
                        "event_type":        "SLA_Breach",
                        "event_at":          case["sla_deadline"].isoformat(),
                        "performed_by":      "System",
                        "sla_compliant":     False,
                        "resolution_reason": None,
                        "escalation_reason": None,
                        "loss_amount":       None,
                        "notes":             "SLA deadline passed without resolution.",
                    })

                # Loss calculation
                loss_rate  = LOSS_RATE_BY_DECISION.get(log["decision"], 0)
                loss_amount = round(case["case_amount"] * loss_rate, 2) if loss_rate > 0 else None

                audit_rows.append({
                    "audit_id":          f"AUD-{uuid.uuid4().hex[:10].upper()}",
                    "case_id":           case_id,
                    "event_type":        "Resolution",
                    "event_at":          resolved_at.isoformat(),
                    "performed_by":      log["changed_by"],
                    "sla_compliant":     bool(sla_compliant),
                    "resolution_reason": log["decision"],
                    "escalation_reason": None,
                    "loss_amount":       loss_amount,
                    "notes":             log["notes"],
                })

    audit_df = pd.DataFrame(audit_rows)

    con.execute("DELETE FROM audit_trail")
    con.register("audit_stage", audit_df)
    con.execute("INSERT INTO audit_trail SELECT * FROM audit_stage")

    # SLA compliance summary
    resolutions = audit_df[audit_df["event_type"] == "Resolution"]
    if len(resolutions) > 0:
        sla_rate = resolutions["sla_compliant"].mean()
        total_loss = resolutions["loss_amount"].sum()
        print(f"  Audit events created:  {len(audit_df):,}")
        print(f"  SLA compliance rate:   {sla_rate:.1%}")
        print(f"  Total confirmed losses: ${total_loss:,.2f}")

    con.close()
    print("Layer 6 complete.\n")


if __name__ == "__main__":
    run()
