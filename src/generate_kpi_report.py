"""
generate_kpi_report.py
Enterprise Marketing Analytics & Customer 360 Platform

Purpose: Query KPI views from DuckDB and export weekly_kpi_report.xlsx.

Usage:
    python src/generate_kpi_report.py
"""

from datetime import datetime
from pathlib import Path

import duckdb

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "olist_analytics.duckdb"
REPORT_PATH = PROJECT_ROOT / "reports" / "weekly_kpi_report.xlsx"

# KPI views to include in the executive summary sheet
KPI_VIEWS = [
    ("Executive Snapshot", "kpi_executive_snapshot"),
    ("Revenue by Month", "kpi_revenue_by_month"),
    ("Revenue by Category", "kpi_revenue_by_category"),
    ("Repeat Purchase Rate", "kpi_repeat_purchase_rate"),
    ("Avg Review Score", "kpi_avg_review_score"),
    ("Delivery Delay Rate", "kpi_delivery_delay_rate"),
    ("Customer Segments", "vw_segment_summary"),
]


def get_connection() -> duckdb.DuckDBPyConnection:
    """Return DuckDB connection. Raises if database does not exist."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}\n"
            "Run data_cleaning.py and load_to_database.py first."
        )
    return duckdb.connect(str(DB_PATH), read_only=True)


def query_view(conn: duckdb.DuckDBPyConnection, view_name: str):
    """
    Query a SQL view and return results as a DataFrame.
    Returns None if view does not exist or has no data yet.
    """
    import pandas as pd

    try:
        return conn.execute(f"SELECT * FROM {view_name}").fetchdf()
    except Exception as exc:
        print(f"  Skipped {view_name}: {exc}")
        return None


def build_report(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Build multi-sheet Excel workbook with KPI data.
    Does not write fake numbers — sheets are omitted if views are empty/missing.
    """
    import pandas as pd

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(REPORT_PATH, engine="openpyxl") as writer:
        # Metadata sheet
        meta = pd.DataFrame(
            {
                "field": ["report_generated_at", "data_source", "database"],
                "value": [
                    datetime.now().isoformat(timespec="seconds"),
                    "Olist Brazilian E-Commerce",
                    str(DB_PATH),
                ],
            }
        )
        meta.to_excel(writer, sheet_name="Report Info", index=False)

        sheets_written = 0
        for sheet_name, view_name in KPI_VIEWS:
            df = query_view(conn, view_name)
            if df is not None and not df.empty:
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                sheets_written += 1
                print(f"  Sheet: {sheet_name} ({len(df)} rows)")

        if sheets_written == 0:
            print(
                "PLACEHOLDER: No KPI views returned data.\n"
                "Populate the database and uncomment SQL views in sql/04_kpi_queries.sql"
            )

    if sheets_written > 0:
        print(f"Report saved: {REPORT_PATH}")


def main() -> None:
    """Generate weekly KPI Excel report."""
    print("Generating weekly KPI report...")
    conn = get_connection()
    try:
        build_report(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
