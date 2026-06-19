"""
Master pipeline runner.
Executes all ETL layers in order from raw data to executive KPIs.

Usage:
    python etl/run_pipeline.py
"""

import os
import sys
import time

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from database.db_utils import init_database


def step(label: str, fn):
    print(f"\n{'-'*60}")
    print(f"  {label}")
    print(f"{'-'*60}")
    t0 = time.time()
    fn()
    print(f"  Done in {time.time()-t0:.1f}s")


def generate_data():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "generate_data",
        os.path.join(PROJECT_ROOT, "data", "generate_data.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()


def load_transactions():
    import pandas as pd
    from database.db_utils import get_connection

    raw_path = os.path.join(PROJECT_ROOT, "data", "raw", "transactions.csv")
    df = pd.read_csv(raw_path, parse_dates=["transaction_date"])
    df["is_international"] = df["is_international"].astype(bool)

    con = get_connection()
    con.execute("DELETE FROM transactions")
    con.register("txn_stage", df)
    con.execute("INSERT INTO transactions SELECT * FROM txn_stage")
    n = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    print(f"  Loaded {n:,} transactions.")
    con.close()


def main():
    print("=" * 60)
    print("  FRAUD DETECTION & RISK OPERATIONS PLATFORM")
    print("  Pipeline Initialisation")
    print("=" * 60)

    print("\nInitialising database schema...")
    init_database()

    raw_path = os.path.join(PROJECT_ROOT, "data", "raw", "transactions.csv")
    if not os.path.exists(raw_path):
        step("Generating synthetic transaction data", generate_data)
    else:
        print("\nRaw data found - skipping generation.")

    step("Loading transactions -> database", load_transactions)

    # Import and run each layer
    import importlib

    layers = [
        ("Layer 1+2 : Fraud Scoring & Risk Tiering", "etl.01_fraud_scoring"),
        ("Layer 3   : Case Assignment",              "etl.02_case_assignment"),
        ("Layer 4   : Investigation Workflow",       "etl.03_investigation_workflow"),
        ("Layer 5   : Fraud Watchlist",              "etl.04_fraud_watchlist"),
        ("Layer 6   : Escalation & Audit Trail",     "etl.05_escalation_audit"),
        ("Layer 7   : Executive KPIs",               "etl.06_executive_kpis"),
    ]

    for label, module_path in layers:
        # Load module from file to avoid dotted-name issues with numeric prefixes
        filename = module_path.split(".")[-1] + ".py"
        filepath = os.path.join(PROJECT_ROOT, "etl", filename)
        spec = importlib.util.spec_from_file_location(module_path, filepath)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        step(label, mod.run)

    print("\n" + "=" * 60)
    print("  Pipeline complete.")
    print("  Launch dashboard:  streamlit run dashboard/app.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
