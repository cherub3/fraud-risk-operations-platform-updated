# Fraud Detection & Risk Operations Platform

A portfolio project demonstrating end-to-end fraud operations: detection, risk tiering, case management, early-warning watchlist, escalation governance, and executive reporting.

**Built for:** Banking, Fraud Analytics, Risk Operations, and Business Analyst roles.

---

## What This Is

Most fraud projects stop at model accuracy. This one starts there and builds the full operational pipeline:

```
Transaction → Fraud Score → Risk Tier → Case Assignment → Investigation
           → Fraud Watchlist → Escalation → Resolution → Executive Reporting
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the pipeline
```bash
python etl/run_pipeline.py
```

### 3. Launch the dashboard
```bash
streamlit run dashboard/app.py
```

---

## Project Structure

```
fraud-risk-platform/
├── data/
│   ├── generate_data.py
│   ├── raw/
│   └── outputs/
├── database/
│   ├── schema.sql
│   ├── db_utils.py
│   └── fraud_platform.duckdb
├── etl/
│   ├── run_pipeline.py
│   ├── 01_fraud_scoring.py
│   ├── 02_case_assignment.py
│   ├── 03_investigation_workflow.py
│   ├── 04_fraud_watchlist.py
│   ├── 05_escalation_audit.py
│   └── 06_executive_kpis.py
├── dashboard/
│   ├── app.py
│   ├── components/data_loader.py
│   └── pages/
│       ├── page1_executive.py
│       ├── page2_watchlist.py
│       ├── page3_cases.py
│       ├── page4_patterns.py
│       └── page5_review.py
└── docs/
    ├── EXECUTIVE_SUMMARY.md
    ├── KEY_FINDINGS.md
    ├── MONTHLY_FRAUD_REVIEW.md
    ├── INTERVIEW_NOTES.md
    └── RESUME_ASSETS.md
```

---

## Platform Layers

| Layer | What It Does |
|---|---|
| 1 — Fraud Detection | Scores every transaction 0–100, assigns fraud label |
| 2 — Risk Tiering | Maps score to Low / Medium / High / Critical |
| 3 — Case Assignment | Creates cases for High/Critical alerts with SLA deadlines |
| 4 — Investigation | Tracks case lifecycle: Open → Investigating → Escalated → Resolved |
| 5 — Fraud Watchlist | Early-warning: flags accounts before fraud is confirmed |
| 6 — Escalation & Audit | Records every event with timestamps for governance |
| 7 — Executive KPIs | Detection, operations, and financial impact KPIs |
| 8 — Monthly Review | Management report: what happened, why, what to do |

---

## Database Schema (6 tables)

| Table | Purpose |
|---|---|
| `transactions` | Raw transaction records |
| `fraud_scores` | Score, probability, label, risk tier |
| `fraud_cases` | Case management with SLA and investigator |
| `investigation_log` | Status history and decisions |
| `fraud_watchlist` | Account-level trend monitoring |
| `audit_trail` | Escalation, resolution, SLA compliance |

---

## Tech Stack

Python · Pandas · DuckDB · Streamlit · Plotly

---

## Documentation

- [BUSINESS_PROBLEM.md](BUSINESS_PROBLEM.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/EXECUTIVE_SUMMARY.md](docs/EXECUTIVE_SUMMARY.md)
- [docs/KEY_FINDINGS.md](docs/KEY_FINDINGS.md)
- [docs/MONTHLY_FRAUD_REVIEW.md](docs/MONTHLY_FRAUD_REVIEW.md)
- [docs/INTERVIEW_NOTES.md](docs/INTERVIEW_NOTES.md)
- [docs/RESUME_ASSETS.md](docs/RESUME_ASSETS.md)
