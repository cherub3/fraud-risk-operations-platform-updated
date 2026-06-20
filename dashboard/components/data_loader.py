"""
Shared data loading utilities for dashboard pages.
All DB reads go through here — cached for Streamlit performance.
"""

import streamlit as st
import pandas as pd
import duckdb
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

DB_PATH  = os.path.join(PROJECT_ROOT, "database", "fraud_platform.duckdb")
KPI_PATH = os.path.join(PROJECT_ROOT, "data", "outputs", "executive_kpis.json")


def _con():
    return duckdb.connect(DB_PATH, read_only=True)


@st.cache_data(ttl=300)
def load_kpis() -> dict:
    if not os.path.exists(KPI_PATH):
        return {}
    with open(KPI_PATH) as f:
        return json.load(f)


@st.cache_data(ttl=300)
def load_fraud_scores() -> pd.DataFrame:
    con = _con()
    try:
        df = con.execute("""
            SELECT fs.*, t.account_id, t.amount, t.transaction_date,
                   t.merchant_category, t.transaction_type, t.location_country,
                   t.hour_of_day, t.true_label, t.is_international
            FROM fraud_scores fs
            JOIN transactions t ON fs.transaction_id = t.transaction_id
        """).df()
    finally:
        con.close()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df


@st.cache_data(ttl=300)
def load_cases() -> pd.DataFrame:
    con = _con()
    try:
        df = con.execute("SELECT * FROM fraud_cases").df()
    finally:
        con.close()
    df["assigned_at"]  = pd.to_datetime(df["assigned_at"])
    df["sla_deadline"] = pd.to_datetime(df["sla_deadline"])
    return df


@st.cache_data(ttl=300)
def load_investigation_log() -> pd.DataFrame:
    con = _con()
    try:
        df = con.execute("SELECT * FROM investigation_log").df()
    finally:
        con.close()
    df["changed_at"] = pd.to_datetime(df["changed_at"])
    return df


@st.cache_data(ttl=300)
def load_watchlist() -> pd.DataFrame:
    con = _con()
    try:
        df = con.execute("SELECT * FROM fraud_watchlist").df()
    finally:
        con.close()
    return df


@st.cache_data(ttl=300)
def load_audit_trail() -> pd.DataFrame:
    con = _con()
    try:
        df = con.execute("SELECT * FROM audit_trail").df()
    finally:
        con.close()
    df["event_at"] = pd.to_datetime(df["event_at"])
    return df


@st.cache_data(ttl=300)
def load_transactions() -> pd.DataFrame:
    con = _con()
    try:
        df = con.execute("SELECT * FROM transactions").df()
    finally:
        con.close()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df
