# Resume Assets
**Fraud Detection & Risk Operations Platform**

---

## Resume Bullet Points

Use these on your CV under a "Projects" section. Choose 3–4 depending on space.

---

### Option Set A — Operations Focus

- Built an end-to-end fraud operations platform covering the full lifecycle: detection, risk tiering, case assignment, investigation workflow, escalation, and executive reporting, processing 50,000 simulated transactions across 500 accounts
- Designed a proactive Fraud Watchlist using three behavioral trend signals (alert frequency, fraud score, merchant diversity) to identify at-risk accounts before fraud confirmation — mirroring early-warning approaches used in retail banking credit risk
- Engineered a case management system with priority-based SLA tracking (P1: 4h / P2: 24h / P3: 72h), investigator assignment, case aging classification, and full audit trail for regulatory compliance simulation
- Developed an executive KPI framework quantifying fraud operations in financial terms: loss exposure, loss avoided, false positive investigation cost, and SLA compliance — enabling C-suite-ready reporting

---

### Option Set B — Technical Focus

- Developed a rule-based fraud scoring engine (0–100 scale, 7 risk signals) producing explainable fraud labels and risk tiers, stored in DuckDB via a 6-table relational schema and surfaced in a 5-page Streamlit dashboard
- Built an ETL pipeline in Python/Pandas covering fraud scoring, case generation, investigation lifecycle simulation, watchlist computation, and executive KPI aggregation across 50,000 transaction records
- Created interactive Plotly visualisations including a fraud alert heatmap (hour × day), weekly trend charts, risk tier distribution, investigator workload, and SLA breach timeline

---

### Option Set C — Risk & Business Focus

- Simulated a complete banking fraud operations workflow including alert triage, investigator case queues, SLA governance, and management reporting — demonstrating business understanding beyond model accuracy
- Built a Fraud Watchlist early-warning system that monitors account-level behavioral signals to predict fraud risk 7–14 days before confirmation, reflecting proactive risk management principles from retail banking
- Designed executive reporting covering Detection, Operations, and Risk KPI categories, including potential loss exposure and false positive cost quantification

---

## LinkedIn Project Description

**Fraud Detection & Risk Operations Platform**

A portfolio project that goes beyond fraud modeling to simulate a complete fraud operations environment.

Most fraud projects end at model accuracy. This one starts there and builds the full operational pipeline a banking fraud team actually runs:

→ Rule-based fraud scoring (7 risk signals, 0–100 score, explainable decisions)
→ Risk tiering (Low / Medium / High / Critical)
→ Case management (investigator assignment, SLA tracking, case aging)
→ Investigation workflow (Open → Investigating → Escalated → Resolved)
→ Proactive Fraud Watchlist (early-warning on rising risk accounts)
→ Escalation & audit trail (governance and compliance simulation)
→ Executive reporting (loss exposure, SLA compliance, financial KPIs)

Built with Python, Pandas, DuckDB, Streamlit, and Plotly.

The goal was to demonstrate fraud operations thinking — prioritization, accountability, escalation, and financial impact reporting — not just data science.

---

## Skills Demonstrated

| Skill | Evidence |
|---|---|
| Fraud Analytics | Rule-based scoring engine, risk tiering, alert analysis |
| Risk Operations | Case management, SLA tracking, aging classification |
| Early Warning Systems | 3-signal watchlist, trend computation, proactive flagging |
| Case Management | Full lifecycle: Open → Investigating → Escalated → Resolved |
| Executive Reporting | KPIs across detection, operations, and financial impact |
| Operational Controls | Audit trail, SLA compliance, escalation governance |
| Data Engineering | ETL pipeline, DuckDB schema, 6-table relational model |
| Dashboard Development | 5-page Streamlit app, Plotly charts |
| Business Communication | Executive summary, key findings, monthly management report |

---

## Roles This Project Targets

- **Fraud Analyst / Fraud Risk Analyst** — directly relevant; demonstrates core fraud operations skills
- **Risk Analyst / Risk Operations** — case management, SLA, escalation, and reporting
- **Business Analyst (Banking)** — business problem framing, operational workflow design, KPI definition
- **Data Analyst (Financial Services)** — ETL, SQL, Python, dashboard development
- **Credit Risk / Operational Risk Analyst** — watchlist methodology, trend signals, loss exposure quantification
- **Compliance Analyst** — audit trail, governance, SLA tracking
- **Graduate Programmes (Banking)** — demonstrates end-to-end business thinking, not just technical execution

---

## How to Talk About This Project in Interviews

**Opening statement (use when asked "tell me about a project"):**

"I built a fraud operations platform that simulates the complete workflow a banking fraud team runs — from fraud detection through to case management, escalation, and executive reporting. Most portfolio projects stop at model accuracy. I wanted to show I understand the operational problem: fraud teams aren't just running models, they're managing investigators, tracking SLAs, reporting to leadership, and trying to prevent fraud before it's confirmed. The most interesting part was building the Fraud Watchlist — an early-warning system that monitors behavioral trend signals to flag accounts at rising risk before any fraud event is confirmed."

**If asked to go deeper:** refer to the specific layer in INTERVIEW_NOTES.md for that topic.

**If asked what you'd do differently:** "Add real-time streaming and a proper ML model as the scoring foundation, with the rules as adjustments. But for demonstrating business logic and risk operations thinking, the current approach is actually more transparent."
