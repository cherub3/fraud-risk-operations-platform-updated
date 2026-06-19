"""
Database utilities — DuckDB connection and schema initialisation.
"""

import duckdb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fraud_platform.duckdb")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(DB_PATH, read_only=read_only)
    return con


def init_database():
    con = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    # Execute each statement separately
    for stmt in schema_sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            try:
                con.execute(stmt)
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"Schema warning: {e}")
    con.close()
    print(f"Database initialised: {DB_PATH}")


if __name__ == "__main__":
    init_database()
