-- ============================================================
-- Fraud Detection & Risk Operations Platform
-- Database Schema
-- ============================================================

-- --------------------------------------------------------
-- TABLE 1: transactions
-- Raw transaction records — the platform input
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id      VARCHAR PRIMARY KEY,
    account_id          VARCHAR NOT NULL,
    transaction_date    TIMESTAMP NOT NULL,
    amount              DECIMAL(12, 2) NOT NULL,
    merchant_id         VARCHAR NOT NULL,
    merchant_category   VARCHAR NOT NULL,
    transaction_type    VARCHAR NOT NULL,   -- POS, Online, ATM, Transfer
    location_country    VARCHAR NOT NULL,
    is_international    BOOLEAN NOT NULL,
    hour_of_day         INTEGER NOT NULL,   -- 0-23
    day_of_week         INTEGER NOT NULL,   -- 0=Mon, 6=Sun
    account_age_days    INTEGER NOT NULL,
    true_label          INTEGER NOT NULL    -- 1 = actual fraud, 0 = not fraud (ground truth)
);

-- --------------------------------------------------------
-- TABLE 2: fraud_scores
-- Layer 1 + 2 output: detection scores and risk tier
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS fraud_scores (
    score_id            VARCHAR PRIMARY KEY,
    transaction_id      VARCHAR NOT NULL REFERENCES transactions(transaction_id),
    fraud_score         DECIMAL(5, 2) NOT NULL,     -- 0.00 to 100.00
    fraud_probability   DECIMAL(5, 4) NOT NULL,     -- 0.0000 to 1.0000
    fraud_label         VARCHAR NOT NULL,            -- Fraud / Not Fraud
    risk_tier           VARCHAR NOT NULL,            -- Low / Medium / High / Critical
    score_components    VARCHAR,                     -- JSON-like string of contributing signals
    scored_at           TIMESTAMP NOT NULL
);

-- --------------------------------------------------------
-- TABLE 3: fraud_cases
-- Layer 3 output: case assignment and SLA tracking
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS fraud_cases (
    case_id             VARCHAR PRIMARY KEY,
    transaction_id      VARCHAR NOT NULL REFERENCES transactions(transaction_id),
    account_id          VARCHAR NOT NULL,
    fraud_score         DECIMAL(5, 2) NOT NULL,
    risk_tier           VARCHAR NOT NULL,
    assigned_investigator VARCHAR NOT NULL,
    priority            VARCHAR NOT NULL,            -- P1 / P2 / P3
    assigned_at         TIMESTAMP NOT NULL,
    sla_deadline        TIMESTAMP NOT NULL,          -- based on priority
    current_status      VARCHAR NOT NULL DEFAULT 'Open',
    case_amount         DECIMAL(12, 2) NOT NULL,
    aging_status        VARCHAR                      -- Fresh / Aging / Critical Aging
);

-- --------------------------------------------------------
-- TABLE 4: investigation_log
-- Layer 4 output: status changes and final decision
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS investigation_log (
    log_id              VARCHAR PRIMARY KEY,
    case_id             VARCHAR NOT NULL REFERENCES fraud_cases(case_id),
    status_from         VARCHAR NOT NULL,
    status_to           VARCHAR NOT NULL,
    changed_at          TIMESTAMP NOT NULL,
    changed_by          VARCHAR NOT NULL,
    decision            VARCHAR,                     -- Fraud / False Positive / Inconclusive / NULL
    notes               VARCHAR
);

-- --------------------------------------------------------
-- TABLE 5: fraud_watchlist
-- Layer 5 output: early-warning system by account
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS fraud_watchlist (
    watchlist_id        VARCHAR PRIMARY KEY,
    account_id          VARCHAR NOT NULL UNIQUE,
    watchlist_status    VARCHAR NOT NULL,            -- Active / Monitoring / Cleared
    risk_trend          VARCHAR NOT NULL,            -- Increasing / Stable / Decreasing
    alert_freq_trend    VARCHAR NOT NULL,            -- Up / Stable / Down
    score_trend         VARCHAR NOT NULL,            -- Up / Stable / Down
    merchant_div_trend  VARCHAR NOT NULL,            -- Up / Stable / Down
    watchlist_reason    VARCHAR NOT NULL,
    recommended_action  VARCHAR NOT NULL,
    priority            VARCHAR NOT NULL,            -- High / Medium / Low
    added_at            TIMESTAMP NOT NULL,
    last_reviewed       TIMESTAMP NOT NULL,
    alert_count_30d     INTEGER,
    avg_fraud_score_30d DECIMAL(5, 2),
    merchant_count_30d  INTEGER
);

-- --------------------------------------------------------
-- TABLE 6: audit_trail
-- Layer 6 output: escalations, resolutions, compliance
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_trail (
    audit_id            VARCHAR PRIMARY KEY,
    case_id             VARCHAR NOT NULL REFERENCES fraud_cases(case_id),
    event_type          VARCHAR NOT NULL,            -- Escalation / Resolution / SLA_Breach / Assignment
    event_at            TIMESTAMP NOT NULL,
    performed_by        VARCHAR NOT NULL,
    sla_compliant       BOOLEAN,
    resolution_reason   VARCHAR,                     -- Fraud Confirmed / False Positive / Insufficient Evidence
    escalation_reason   VARCHAR,
    loss_amount         DECIMAL(12, 2),
    notes               VARCHAR
);

-- --------------------------------------------------------
-- INDEXES for query performance
-- --------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_transactions_account  ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date     ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_fraud_scores_txn      ON fraud_scores(transaction_id);
CREATE INDEX IF NOT EXISTS idx_fraud_scores_tier     ON fraud_scores(risk_tier);
CREATE INDEX IF NOT EXISTS idx_cases_status          ON fraud_cases(current_status);
CREATE INDEX IF NOT EXISTS idx_cases_account         ON fraud_cases(account_id);
CREATE INDEX IF NOT EXISTS idx_cases_investigator    ON fraud_cases(assigned_investigator);
CREATE INDEX IF NOT EXISTS idx_watchlist_status      ON fraud_watchlist(watchlist_status);
CREATE INDEX IF NOT EXISTS idx_audit_case            ON audit_trail(case_id);
