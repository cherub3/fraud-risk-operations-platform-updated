# Interview Notes
**Fraud Detection & Risk Operations Platform**
*Prepared for banking, risk, and analytics interviews*

---

## How to Use This Document

For each major platform component, this document provides:
- **Business Question** — what an interviewer is actually probing
- **Your Answer** — what you built and why
- **Business Value** — why it matters to the bank
- **30-Second Explanation** — what to say if asked to summarise on the spot

Practice the 30-second explanations until they feel natural. Interviewers at banks are assessing whether you think like a risk professional, not just a coder.

---

## Layer 1+2: Fraud Detection & Risk Tiering

**Business Question:**
"How does your fraud model work? How do you decide what's fraud?"

**Your Answer:**
I built a rule-based scoring engine that evaluates each transaction against seven risk signals: transaction amount, international flag, hour of day, merchant category risk, transaction type, account age, and velocity. Each signal contributes a weighted component to a 0–100 fraud score. The score is then mapped to a risk tier — Low, Medium, High, or Critical — using predefined business thresholds.

I deliberately chose rule-based scoring over a black-box ML model for two reasons. First, in banking, every fraud decision needs to be explainable — to investigators, to customers, and to regulators. Second, for a portfolio project, explainable scoring demonstrates risk thinking better than accuracy metrics alone.

**Business Value:**
Risk tiering is the operational translation of fraud detection. Without it, every alert looks the same and investigators don't know what to open first. Tiering creates priority — Critical cases get investigated in 4 hours, Low alerts are logged but not cased.

**30-Second Explanation:**
"My fraud model scores every transaction from 0 to 100 based on seven risk signals — things like transaction amount, time of day, merchant category, and whether it's international. Each score maps to a risk tier: Low, Medium, High, or Critical. Only High and Critical alerts generate investigation cases — this stops the team from drowning in false positives and ensures the most dangerous transactions get looked at first."

---

## Layer 3: Case Assignment

**Business Question:**
"How do you manage the investigator workflow? How do you stop cases falling through the cracks?"

**Your Answer:**
Every High and Critical alert is automatically converted into a fraud case with a unique case ID, assigned investigator, priority level, and SLA deadline. P1 (Critical) cases have a 4-hour SLA, P2 (High) have 24 hours. Investigators are assigned round-robin within priority tier to balance workload. The platform tracks case aging — Fresh, Aging, Critical Aging — so team leads can see at a glance where the backlog is building.

**Business Value:**
Without formal case management, fraud alerts are emails in an inbox. There's no ownership, no deadline, no accountability. Case management creates the operational infrastructure that turns alerts into outcomes. It also creates the audit trail regulators expect.

**30-Second Explanation:**
"Each fraud alert that clears my scoring threshold automatically becomes a case — with a case ID, an assigned investigator, and a deadline. P1 cases must be resolved within 4 hours. The platform tracks how old each case is, so the team lead can see instantly if cases are aging out of their SLA. This is the difference between fraud detection and fraud operations."

---

## Layer 4: Investigation Workflow

**Business Question:**
"Walk me through how a fraud case moves from open to closed."

**Your Answer:**
Each case follows a defined lifecycle: Open → Investigating → (optionally) Escalated → Resolved. Every status change is logged with a timestamp, the actor who made the change, and notes. When a case is resolved, the investigator records a decision: Fraud Confirmed, False Positive, or Inconclusive. This decision drives the financial reporting — Fraud Confirmed cases contribute to loss figures, False Positives contribute to investigation cost.

**Business Value:**
The investigation log is the audit trail. In a real bank, fraud operations must be able to demonstrate to internal audit and external regulators exactly how every alert was handled, by whom, and when. The lifecycle also enables performance measurement — what's the average time to resolve a Critical case? What's the escalation rate?

**30-Second Explanation:**
"Every case goes through Open, Investigating, optionally Escalated, then Resolved. Every status change is timestamped and logged. At resolution, the investigator records whether it was confirmed fraud, a false positive, or inconclusive. This creates the audit trail the bank needs for compliance and gives leadership the data to measure whether the team is performing."

---

## Layer 5: Fraud Watchlist

**Business Question:**
"How do you prevent fraud before it happens? Most fraud systems are reactive — what makes yours different?"

**Your Answer:**
The Fraud Watchlist is the most differentiating part of this platform. Instead of waiting for confirmed fraud, I monitor three behavioral trend signals per account: alert frequency trend, fraud score trend, and merchant diversity trend. Each signal is computed by comparing the last 30 days to the prior 30 days. Accounts where two or more signals are trending upward are flagged on the watchlist — before a fraud event is confirmed.

This mirrors the approach banks use in credit risk monitoring — you don't wait for a customer to miss a payment before you flag them as a credit risk. You monitor behavioral signals that historically precede defaults.

**Business Value:**
Proactive fraud prevention is structurally more valuable than reactive investigation. Once fraud is confirmed, the loss is often already booked. The watchlist allows the fraud team to intervene — with transaction limits, authentication challenges, or a customer call — while the loss can still be prevented.

**30-Second Explanation:**
"My watchlist monitors three behavioral signals per account — are they generating more fraud alerts? Is their fraud score trending up? Are they suddenly using a lot of different merchants? Accounts with two or more escalating signals get flagged before any fraud is confirmed. This shifts the team from reactive investigation to proactive prevention — which is where the real financial value is."

---

## Layer 6: Escalation & Audit Trail

**Business Question:**
"How does your platform support regulatory compliance and governance?"

**Your Answer:**
Every operationally significant event is written to an audit trail: case assignment, status changes, escalations, resolutions, and SLA breaches. Each record includes a timestamp, the actor, the reason, and a compliance flag. The audit trail is immutable — it cannot be edited. This creates the evidence a bank needs for internal audit, regulatory review, and dispute resolution.

SLA compliance is computed per case at resolution time — was the case closed before the deadline? This feeds the SLA compliance KPI that management monitors monthly.

**Business Value:**
In regulated banking environments, the audit trail is not optional. Internal audit, the FCA/OCC/other regulators, and internal risk committees will periodically review how fraud operations are managed. A platform without audit trails cannot demonstrate process compliance — which is a regulatory risk in itself.

**30-Second Explanation:**
"Every event in the platform — assignments, escalations, resolutions, SLA breaches — is written to an audit log with timestamps and actors. At resolution, we record whether SLA was met. This isn't just good practice — in a regulated bank, audit trails are mandatory. If a regulator asks how a specific fraud case was handled, this log is the answer."

---

## Layer 7: Executive Reporting

**Business Question:**
"How would you report on fraud performance to the CFO or Head of Risk?"

**Your Answer:**
I built the executive dashboard around three KPI categories. Detection KPIs — fraud alert rate, confirmed fraud, false positives — tell leadership whether the model is working. Operations KPIs — open cases, escalations, SLA compliance — tell them whether the team is performing. Risk KPIs — fraud amount caught, potential loss exposure, loss avoided, false positive cost — translate fraud operations into P&L impact, which is the language the CFO speaks.

The key insight is that fraud operations must justify itself financially. "We caught 600 fraud cases" is less compelling than "we prevented $2.3M in losses at a false positive investigation cost of $90,000 — net value protected: $2.21M."

**Business Value:**
Executive reporting closes the accountability loop. Without financial KPIs, the fraud team cannot make the case for headcount, tooling, or process investment. With them, every budget conversation can be framed as a return-on-investment discussion.

**30-Second Explanation:**
"My executive dashboard has three layers: detection metrics, operations metrics, and financial impact. The CFO doesn't care about F1 scores — they care about how much fraud we caught, how much we missed, what our loss exposure is, and what the false positives are costing us. I built the reporting to answer exactly those questions."

---

## Common Behavioural Questions

**"Why did you build this project?"**
"Most fraud projects I saw in portfolios stop at model accuracy. I wanted to build something that showed I understood the operational problem — that a fraud team isn't just running models, they're managing investigators, tracking SLAs, escalating cases, reporting to leadership. I designed this to demonstrate that full operational thinking."

**"What would you do differently?"**
"In a production environment, I'd add real-time transaction streaming — the scoring and case creation would happen in milliseconds, not batch. I'd also want to incorporate a ML model for the base fraud probability and use the rules as adjustments rather than primary signals. But for a portfolio project, the rule-based approach demonstrates the business logic more clearly."

**"What was the hardest part to build?"**
"The watchlist was conceptually the hardest part. It required thinking about fraud risk as a trend, not a point-in-time event. Computing meaningful trend signals from account-level behavioral data — and then translating those trends into a prioritized action list — required thinking like a risk manager, not a data scientist."

**"How would this work in a real bank?"**
"The architecture would be the same — detect, tier, case, investigate, watchlist, report. The tech stack would change: you'd replace batch ETL with a real-time event stream, DuckDB with a scalable data warehouse, and Streamlit with an enterprise BI tool or a purpose-built case management system. But the business logic and the workflow I've built here reflect how actual fraud operations teams run."
