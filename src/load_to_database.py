"""
load_to_database.py
Enterprise Marketing Analytics & Customer 360 Platform

Purpose: Load processed CSVs into DuckDB, build KPI views, and validate results.

Usage:
    python src/load_to_database.py
"""

import re
from pathlib import Path

import duckdb

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
DB_PATH = PROCESSED_DIR / "olist_analytics.duckdb"

# Core analytics tables loaded from processed CSVs
TABLES_TO_LOAD = [
    "customers",
    "orders",
    "order_items",
    "payments",
    "products",
    "reviews",
]

# SQL scripts executed after base tables are loaded (order matters)
ANALYTICS_SQL_SCRIPTS = [
    "04_kpi_queries.sql",
    "05_customer_segmentation.sql",
    "06_dashboard_views.sql",
]

# Smoke-test queries run against real loaded data
VALIDATION_QUERIES = {
    "total_orders_delivered": """
        SELECT COUNT(*) AS value
        FROM orders
        WHERE is_delivered = 1
    """,
    "total_unique_customers": """
        SELECT COUNT(DISTINCT c.customer_unique_id) AS value
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.is_delivered = 1
    """,
    "total_revenue_brl": """
        SELECT ROUND(SUM(oi.price), 2) AS value
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.order_id
        WHERE o.is_delivered = 1
          AND oi.is_valid_price = TRUE
    """,
    "total_payment_value_brl": """
        SELECT ROUND(SUM(payment_value), 2) AS value
        FROM payments
    """,
    "avg_review_score": """
        SELECT ROUND(AVG(review_score), 2) AS value
        FROM reviews
        WHERE is_valid_score = TRUE
    """,
}


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open (or create) the DuckDB analytics database."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def load_processed_csvs(conn: duckdb.DuckDBPyConnection) -> None:
    """Load each processed CSV into a DuckDB table matching the file name."""
    print("\nLoading processed CSVs into DuckDB...")
    for table in TABLES_TO_LOAD:
        csv_path = PROCESSED_DIR / f"{table}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing processed file: {csv_path}")

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT * FROM read_csv(?, header = TRUE, auto_detect = TRUE)
            """,
            [str(csv_path)],
        )
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {row_count:,} rows")


def table_exists(conn: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    """Return True if a table exists in the main schema."""
    result = conn.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'main'
          AND table_name = ?
        """,
        [table_name],
    ).fetchone()[0]
    return result > 0


def validate_tables(conn: duckdb.DuckDBPyConnection) -> None:
    """Confirm every expected base table was created."""
    print("\nValidating base tables...")
    missing = [t for t in TABLES_TO_LOAD if not table_exists(conn, table_name=t)]
    if missing:
        raise RuntimeError(f"Missing tables after load: {', '.join(missing)}")
    print(f"  All {len(TABLES_TO_LOAD)} base tables exist.")


def _strip_sql_comments(sql: str) -> str:
    """Remove line comments so placeholder headers do not block execution."""
    lines = []
    for line in sql.splitlines():
        stripped = re.sub(r"--.*$", "", line).strip()
        if stripped:
            lines.append(stripped)
    return "\n".join(lines)


def run_sql_file(conn: duckdb.DuckDBPyConnection, sql_path: Path) -> None:
    """Execute an analytics SQL file (views / segmentation logic)."""
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    sql = _strip_sql_comments(sql_path.read_text(encoding="utf-8"))
    conn.execute(sql)
    print(f"  Executed: {sql_path.name}")


def run_analytics_sql(conn: duckdb.DuckDBPyConnection) -> None:
    """Build KPI views, segmentation tables, and dashboard views."""
    print("\nBuilding analytics layer (KPIs, segmentation, dashboard views)...")
    for script in ANALYTICS_SQL_SCRIPTS:
        run_sql_file(conn, SQL_DIR / script)


def run_validation_queries(conn: duckdb.DuckDBPyConnection) -> None:
    """Run basic test queries and print real results."""
    print("\nValidation queries (real data):")
    for name, query in VALIDATION_QUERIES.items():
        value = conn.execute(query).fetchone()[0]
        print(f"  {name}: {value}")


def main() -> None:
    """Load processed data, build analytics views, and validate."""
    print(f"DuckDB database: {DB_PATH}")

    conn = get_connection()
    try:
        load_processed_csvs(conn)
        validate_tables(conn)
        run_analytics_sql(conn)
        run_validation_queries(conn)
        print(f"\nDatabase ready: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
