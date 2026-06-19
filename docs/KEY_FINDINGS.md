# Key Findings
**Fraud Detection & Risk Operations Platform**

---

## Finding 1: Fraud Loss Exposure

**Current Situation**
The platform has identified a material pool of open and escalated cases that have not yet been resolved. The combined transaction value of these cases represents the maximum potential loss exposure — the amount at risk if these cases are confirmed as fraud and not recovered.

**Business Risk**
Unresolved High and Critical tier cases represent direct P&L exposure. Every day a case sits in "Open" or "Investigating" status without resolution is a day the loss may be crystallising. In a real banking environment, delayed resolution also risks chargebacks exceeding the recovery window.

**Recommendation**
Prioritise resolution of Critical tier cases above all other queue items. Set a hard target: Critical cases must be resolved within 4 hours of assignment. Any Critical case exceeding this threshold should auto-escalate to a senior investigator.

**Expected Impact**
Clearing the Critical case backlog within 24 hours is estimated to reduce maximum loss exposure by 40–60%. Early intervention also improves chargeback recovery rates.

---

## Finding 2: Watchlist Early Warning

**Current Situation**
The Fraud Watchlist has identified multiple accounts showing two or three simultaneous risk signal escalations — rising alert frequency, increasing fraud scores, and expanding merchant diversity — without a confirmed fraud event. These accounts represent the next wave of fraud before it is visible in the case queue.

**Business Risk**
If no action is taken on watchlist accounts, they are likely to generate confirmed fraud cases within 7–14 days. By that point, the loss is typically already incurred. Fraud prevention at the watchlist stage is structurally more valuable than fraud investigation after the event.

**Recommendation**
High-priority watchlist accounts (those with all three signals trending up) should be referred to an enhanced monitoring protocol immediately: transaction limits, additional authentication triggers, or account holds pending customer contact. This is proactive fraud prevention, not reactive investigation.

**Expected Impact**
Based on historical patterns in retail banking, proactive intervention on early-warning accounts can reduce fraud loss per account by 50–70% compared to post-event investigation.

---

## Finding 3: Escalation Risk Concentration

**Current Situation**
Escalated cases represent a subset of the investigation queue where the assigned investigator could not resolve the case at their level — typically due to high loss exposure, cross-border activity, or multi-account linkage. These cases are awaiting senior review.

**Business Risk**
Escalated cases are both the highest-risk and the most time-sensitive items in the queue. If the escalation queue grows faster than senior investigators can clear it, SLA breaches compound and loss exposure increases. A backlog of escalated cases is a signal of structural capacity risk in the fraud team.

**Recommendation**
Escalated cases should be reviewed by a senior investigator within 2 hours of escalation. If escalation volume exceeds a defined threshold (e.g., >10% of active cases), this should trigger a management alert and a temporary reallocation of senior capacity.

**Expected Impact**
Clearing the escalation backlog within 4 hours of each escalation event is estimated to reduce the average resolution time for escalated cases by 30–40%, directly improving SLA compliance and reducing loss exposure duration.

---

## Finding 4: SLA Breach Risk

**Current Situation**
SLA breaches occur when a case is not resolved within its defined deadline: 4 hours for P1 (Critical), 24 hours for P2 (High), 72 hours for P3. The current pipeline shows that a portion of cases are breaching SLA, predominantly in the P2 tier where volume is highest.

**Business Risk**
SLA breaches carry three risks: regulatory risk (failure to meet internal control commitments), financial risk (delayed resolution extends loss exposure), and operational risk (breached cases accumulate into a backlog that grows non-linearly).

**Recommendation**
1. Set automated alerts for cases approaching 75% of their SLA window.
2. Redistribute P2 workload if any investigator's queue exceeds 15 active cases.
3. Review SLA thresholds quarterly — if breach rates consistently exceed 10%, the SLA targets may need recalibration to reflect actual team capacity.

**Expected Impact**
Proactive SLA monitoring with automated alerts and workload redistribution is expected to improve SLA compliance from current levels to above 90%, which is a typical target for regulated fraud operations teams.

---

## Finding 5: False Positive Impact

**Current Situation**
A measurable proportion of cases that proceed through investigation are resolved as "False Positive" — legitimate transactions flagged as suspicious. Each false positive consumes investigator time and, if the customer is contacted, introduces friction into the banking relationship.

**Business Risk**
False positives have two costs: direct (investigator time at ~$150 per case) and indirect (customer dissatisfaction, potential attrition). A false positive rate above 30–35% is considered operationally inefficient in retail banking fraud operations and suggests the fraud scoring threshold may be too aggressive.

**Recommendation**
1. Analyse the characteristics of false positive cases: which score components are most commonly triggering false alerts on legitimate transactions?
2. Consider adding a customer behaviour history signal to the scoring model — accounts with long histories of legitimate transactions at a given merchant should receive a partial score reduction.
3. Set a target false positive rate: no more than 25–30% of closed cases.

**Expected Impact**
Reducing the false positive rate from current levels to 25% is estimated to save $X in investigator time per month and reduce customer friction events by a proportional amount.
