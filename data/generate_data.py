"""
Synthetic Data Generator
Fraud Detection & Risk Operations Platform

Generates 90 days of realistic transaction data with:
- Normal account behavior patterns
- Fraud accounts with suspicious behavior
- High-risk accounts for watchlist testing
- Realistic merchant activity and time patterns
"""

import pandas as pd
import numpy as np
import random
import uuid
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

# ── Config ──────────────────────────────────────────────────────────────────

NUM_ACCOUNTS        = 500
NUM_TRANSACTIONS    = 50_000
FRAUD_RATE          = 0.025          # 2.5% ground-truth fraud
HIGH_RISK_ACCOUNTS  = 40             # accounts that will appear on watchlist
DAYS_HISTORY        = 90
OUTPUT_DIR          = os.path.join(os.path.dirname(__file__), "raw")
START_DATE          = datetime.now() - timedelta(days=DAYS_HISTORY)

MERCHANT_CATEGORIES = [
    "Grocery", "Fuel", "Restaurant", "Online Retail",
    "Electronics", "Travel", "ATM", "Healthcare",
    "Entertainment", "Luxury Goods", "Cryptocurrency",
    "Money Transfer", "Gaming", "Utilities"
]

TRANSACTION_TYPES = ["POS", "Online", "ATM", "Transfer"]

COUNTRIES = {
    "domestic": ["US"] * 80 + ["CA"] * 10 + ["GB"] * 5 + ["AU"] * 5,
    "international": ["RU", "NG", "CN", "BR", "UA", "RO", "VN", "MX"]
}

INVESTIGATORS = [
    "Sarah Chen", "Marcus Johnson", "Priya Patel",
    "Tom Walsh", "Aisha Okafor", "David Kim"
]


# ── Helper functions ─────────────────────────────────────────────────────────

def gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def weighted_hour() -> int:
    """Normal transactions cluster during business hours; fraud spikes at night."""
    hours = list(range(24))
    weights = [
        1, 1, 1, 1, 1, 2,       # 0-5   night (low)
        4, 6, 8, 9, 9, 10,      # 6-11  morning ramp
        10, 10, 9, 9, 9, 10,    # 12-17 business hours
        9, 8, 7, 5, 3, 2        # 18-23 evening taper
    ]
    return random.choices(hours, weights=weights)[0]


def fraud_hour() -> int:
    """Fraud skews to late night / early morning."""
    hours = list(range(24))
    weights = [
        8, 9, 9, 8, 7, 5,
        3, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 3,
        4, 5, 6, 7, 7, 8
    ]
    return random.choices(hours, weights=weights)[0]


def normal_amount() -> float:
    """Normal transaction amounts — right-skewed log-normal."""
    return round(np.random.lognormal(mean=3.8, sigma=1.1), 2)


def fraud_amount() -> float:
    """Fraud transactions tend toward higher amounts."""
    return round(np.random.lognormal(mean=5.2, sigma=1.3), 2)


# ── Account profiles ─────────────────────────────────────────────────────────

def build_account_profiles(n_accounts: int, n_high_risk: int) -> pd.DataFrame:
    account_types = (
        ["normal"] * (n_accounts - n_high_risk - int(n_accounts * FRAUD_RATE * 2))
        + ["high_risk"] * n_high_risk
        + ["fraud"] * int(n_accounts * FRAUD_RATE * 2)
    )
    # pad if needed
    while len(account_types) < n_accounts:
        account_types.append("normal")

    random.shuffle(account_types)
    account_ids = [f"ACC{str(i).zfill(5)}" for i in range(1, n_accounts + 1)]
    age_days = np.random.randint(30, 3650, size=n_accounts)

    return pd.DataFrame({
        "account_id":   account_ids,
        "account_type": account_types[:n_accounts],
        "account_age_days": age_days
    })


# ── Transaction generator ────────────────────────────────────────────────────

def generate_transactions(accounts: pd.DataFrame, n_transactions: int) -> pd.DataFrame:
    rows = []

    # Weight account sampling so fraud/high-risk accounts generate more transactions
    type_weights = {"normal": 1.0, "high_risk": 2.5, "fraud": 3.0}
    weights = [type_weights[t] for t in accounts["account_type"]]
    total_w = sum(weights)
    probs = [w / total_w for w in weights]

    sampled_accounts = accounts.sample(
        n=n_transactions, replace=True, weights=probs
    ).reset_index(drop=True)

    for i, acc in sampled_accounts.iterrows():
        acc_id    = acc["account_id"]
        acc_type  = acc["account_type"]
        acc_age   = int(acc["account_age_days"])

        # Is this transaction fraudulent?
        if acc_type == "fraud":
            is_fraud = random.random() < 0.35
        elif acc_type == "high_risk":
            is_fraud = random.random() < 0.08
        else:
            is_fraud = random.random() < 0.005

        # Time
        days_ago  = random.randint(0, DAYS_HISTORY - 1)
        hour      = fraud_hour() if is_fraud else weighted_hour()
        txn_date  = START_DATE + timedelta(
            days=days_ago,
            hours=hour,
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        # Amount
        amount = fraud_amount() if is_fraud else normal_amount()
        amount = min(amount, 50000.0)

        # Merchant
        if is_fraud:
            risky_cats = ["Online Retail", "Electronics", "Cryptocurrency",
                          "Money Transfer", "Luxury Goods", "ATM", "Gaming"]
            merchant_cat = random.choice(risky_cats)
        else:
            merchant_cat = random.choice(MERCHANT_CATEGORIES)

        merchant_id = f"MER{random.randint(1, 800):04d}"

        # Transaction type
        if merchant_cat in ["ATM"]:
            txn_type = "ATM"
        elif merchant_cat in ["Online Retail", "Cryptocurrency", "Gaming"]:
            txn_type = "Online"
        elif merchant_cat in ["Money Transfer"]:
            txn_type = "Transfer"
        else:
            txn_type = random.choice(["POS", "Online"])

        # Location
        if is_fraud and random.random() < 0.35:
            country = random.choice(COUNTRIES["international"])
            is_intl  = True
        else:
            country = random.choice(COUNTRIES["domestic"])
            is_intl  = country != "US"

        rows.append({
            "transaction_id":    gen_id("TXN"),
            "account_id":        acc_id,
            "transaction_date":  txn_date,
            "amount":            amount,
            "merchant_id":       merchant_id,
            "merchant_category": merchant_cat,
            "transaction_type":  txn_type,
            "location_country":  country,
            "is_international":  is_intl,
            "hour_of_day":       hour,
            "day_of_week":       txn_date.weekday(),
            "account_age_days":  acc_age,
            "true_label":        int(is_fraud)
        })

    df = pd.DataFrame(rows)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df.sort_values("transaction_date").reset_index(drop=True)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Generating account profiles...")
    accounts = build_account_profiles(NUM_ACCOUNTS, HIGH_RISK_ACCOUNTS)

    print(f"Generating {NUM_TRANSACTIONS:,} transactions over {DAYS_HISTORY} days...")
    transactions = generate_transactions(accounts, NUM_TRANSACTIONS)

    actual_fraud_rate = transactions["true_label"].mean()
    print(f"  Fraud rate:        {actual_fraud_rate:.2%}")
    print(f"  Total frauds:      {transactions['true_label'].sum():,}")
    print(f"  Date range:        {transactions['transaction_date'].min().date()} "
          f"→ {transactions['transaction_date'].max().date()}")

    # Save
    txn_path = os.path.join(OUTPUT_DIR, "transactions.csv")
    acc_path = os.path.join(OUTPUT_DIR, "account_profiles.csv")
    transactions.to_csv(txn_path, index=False)
    accounts.to_csv(acc_path, index=False)
    print(f"\nSaved: {txn_path}")
    print(f"Saved: {acc_path}")
    print("Done.")


if __name__ == "__main__":
    main()
