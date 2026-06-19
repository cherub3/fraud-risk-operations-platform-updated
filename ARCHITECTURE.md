# Platform Architecture

## Design Philosophy

This platform is built around a single operational principle: fraud detection alone does not stop fraud. The operational pipeline that follows detection — assessment, assignment, investigation, escalation, and resolution — determines whether a fraud signal becomes a prevented loss or a booked one.

The architecture is intentionally lean. It avoids enterprise complexity while demonstrating the complete fraud operations lifecycle a bank actually runs.

---

## Architecture Overview

```
TRANSACTIONS
     │
     ▼
┌─────────────────────────────┐
│  LAYER 1: FRAUD DETECTION   │  Fraud Score, Probability, Label
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  LAYER 2: RISK TIERING      │  Low / Medium / High / Critical
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  LAYER 3: CASE ASSIGNMENT   │  Case ID, Investigator, SLA
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  LAYER 4: INVESTIGATION     │  Open → Investigating → Escalated → Resolved
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  LAYER 5: FRAUD WATCHLIST   │  Early Warning — Accounts at Risk
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  LAYER 6: ESCALATION &      │  Audit Trail, SLA Compliance
│           RESOLUTION        │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  LAYER 7: EXECUTIVE KPIs    │  Loss Exposure, Fraud Rate, Compliance
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  LAYER 8: MONTHLY REVIEW    │  Management Reporting
└─────────────────────────────┘
```

---

## Layer Descriptions

### Layer 1 — Fraud Detection
**Input:** Raw transactions  
**Process:** Rule-based scoring enriched with behavioral signals (velocity, time-of-day, merchant category)  
**Output:** Fraud Score (0–100), Fraud Probability, Fraud Label (Fraud / Not Fraud)  
**Purpose:** Identify suspicious transactions for investigation.

### Layer 2 — Risk Tiering
**Input:** Fraud Score  
**Process:** Score-to-tier mapping with business-defined thresholds  
**Output:** Risk Tier — Low / Medium / High / Critical  
**Purpose:** Prioritize investigator effort. A Critical tier case demands immediate attention.

### Layer 3 — Case Assignment
**Input:** High and Critical tier alerts  
**Process:** Case generation with round-robin investigator assignment and SLA calculation  
**Output:** Fraud Case with Case ID, Investigator, Priority, Assignment Date, SLA Deadline  
**Purpose:** Create investigator accountability and a trackable case queue.

### Layer 4 — Investigation Workflow
**Input:** Fraud Cases  
**Process:** Status lifecycle management  
**Statuses:** Open → Investigating → Escalated → Resolved  
**Decisions:** Fraud Confirmed / False Positive / Inconclusive  
**Purpose:** Case lifecycle management from alert to decision.

### Layer 5 — Fraud Watchlist
**Input:** Transaction history by account  
**Process:** Three trend signals computed per account:
- Alert Frequency Trend: Is this account generating more alerts over time?
- Fraud Score Trend: Is the average fraud score increasing?
- Merchant Diversity Trend: Is the account suddenly transacting at an unusual spread of merchants?

**Output:** Watchlist Status, Risk Trend, Watchlist Reason, Recommended Action, Priority  
**Purpose:** Proactive early-warning system. Intervene before losses are confirmed.

### Layer 6 — Escalation, Resolution & Audit Trail
**Input:** Resolved and escalated cases  
**Process:** Escalation logging, resolution recording, SLA compliance calculation  
**Output:** Audit log with timestamps, resolution reasons, SLA pass/fail  
**Purpose:** Regulatory compliance, governance, and operational accountability.

### Layer 7 — Executive Reporting
**Input:** All platform outputs  
**Process:** KPI aggregation across detection, operations, and risk dimensions  
**Output:** Executive dashboard with fraud rate, loss exposure, SLA compliance, watchlist volume  
**Purpose:** Give leadership a real-time view of fraud performance.

### Layer 8 — Monthly Fraud Review
**Input:** Monthly aggregated data  
**Process:** Structured narrative generation — What Happened, Why, Business Risk, Recommendations  
**Output:** Management report (markdown rendered in dashboard)  
**Purpose:** Enable leadership to understand fraud trends and make resourcing decisions.

---

## Database Design

**6 core tables:**

| Table | Purpose |
|---|---|
| `transactions` | Raw transaction records |
| `fraud_scores` | Fraud detection output per transaction |
| `fraud_cases` | Case management with assignment and SLA |
| `investigation_log` | Status changes and decisions per case |
| `fraud_watchlist` | Account-level risk trend monitoring |
| `audit_trail` | Escalation and resolution audit records |

---

## Tech Stack

| Component | Technology |
|---|---|
| Data Processing | Python, Pandas |
| Database | DuckDB (embedded SQL, no setup needed) |
| SQL Modeling | SQL via DuckDB |
| Dashboard | Streamlit |
| Charts | Plotly |
| Version Control | Git, GitHub |

---

## What This Architecture Is Not

This is not an enterprise banking system. It does not include:
- Real-time streaming (Kafka, Flink)
- Cloud infrastructure (AWS, GCP)
- API layers or microservices
- ML model training pipelines

These are intentionally excluded. The goal is to demonstrate fraud operations thinking, risk assessment logic, and business reporting — skills that matter in a fraud analytics or risk operations role — using a stack a fresher can build, deploy, and explain confidently.
