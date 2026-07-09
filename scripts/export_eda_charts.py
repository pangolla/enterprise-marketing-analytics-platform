#!/usr/bin/env python3
"""
export_eda_charts.py
Enterprise Marketing Analytics & Customer 360 Platform

Export EDA chart PNGs from DuckDB KPI views into dashboards/screenshots/.

Usage:
    python scripts/export_eda_charts.py
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "olist_analytics.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "dashboards" / "screenshots"

# Views queried for each chart (inspected at runtime)
VIEW_QUERIES = {
    "revenue_trend": "kpi_revenue_by_month",
    "revenue_by_category": "kpi_revenue_by_category",
    "revenue_by_state": "vw_revenue_by_state",
    "delivery_performance": "vw_delivery_performance",
    "review_summary": "vw_review_summary",
    "repeat_purchase_rate": "kpi_repeat_purchase_rate",
}

REPEAT_BREAKDOWN_SQL = """
    SELECT
        CASE
            WHEN order_count = 1 THEN '1 order'
            WHEN order_count = 2 THEN '2 orders'
            ELSE '3+ orders'
        END AS order_bucket,
        COUNT(*) AS customers
    FROM (
        SELECT
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id) AS order_count
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.is_delivered = 1
        GROUP BY c.customer_unique_id
    ) t
    GROUP BY 1
    ORDER BY 1
"""


def require_columns(df: pd.DataFrame, required: list[str], source: str) -> None:
    """Raise a clear error if expected columns are missing."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(
            f"{source} is missing required columns: {missing}. "
            f"Available columns: {list(df.columns)}"
        )


def pick_column(df: pd.DataFrame, candidates: list[str], source: str) -> str:
    """Return the first matching column name from a candidate list."""
    for col in candidates:
        if col in df.columns:
            return col
    raise ValueError(
        f"{source} has none of the expected columns {candidates}. "
        f"Available columns: {list(df.columns)}"
    )


def inspect_view(conn: duckdb.DuckDBPyConnection, view_name: str) -> pd.DataFrame:
    """Load a view and print its columns for debugging."""
    df = conn.execute(f"SELECT * FROM {view_name}").fetchdf()
    print(f"  Loaded {view_name}: {len(df):,} rows, columns={list(df.columns)}")
    return df


def build_period_column(df: pd.DataFrame, source: str) -> pd.Series:
    """Build a sortable period column from year/month when present."""
    if "year" in df.columns and "month" in df.columns:
        return pd.to_datetime(
            df["year"].astype(int).astype(str)
            + "-"
            + df["month"].astype(int).astype(str).str.zfill(2)
            + "-01"
        )
    for col in ("period", "month_name", "full_date", "order_purchase_timestamp"):
        if col in df.columns:
            return pd.to_datetime(df[col], errors="coerce")
    raise ValueError(f"{source} has no usable date columns for trend plotting.")


def save_figure(fig: plt.Figure, filename: str) -> Path:
    """Save a matplotlib figure and return the output path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    fig.savefig(output_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    return output_path


def plot_revenue_trend(df: pd.DataFrame) -> Path:
    require_columns(df, ["revenue"], VIEW_QUERIES["revenue_trend"])
    period = build_period_column(df, VIEW_QUERIES["revenue_trend"])
    plot_df = df.copy()
    plot_df["period"] = period
    plot_df = plot_df.sort_values("period")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(plot_df["period"], plot_df["revenue"], marker="o", linewidth=2, color="#2E86AB")
    ax.set_title("Monthly Revenue Trend (Delivered Orders)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (BRL)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"R${x / 1e6:.1f}M"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    return save_figure(fig, "revenue_trend.png")


def plot_revenue_by_category(df: pd.DataFrame, top_n: int = 10) -> Path:
    require_columns(df, ["revenue"], VIEW_QUERIES["revenue_by_category"])
    category_col = pick_column(
        df, ["category_en", "product_category_name", "category"], VIEW_QUERIES["revenue_by_category"]
    )
    top = df.nlargest(top_n, "revenue").sort_values("revenue")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top[category_col], top["revenue"], color="#A23B72")
    ax.set_title(f"Top {top_n} Product Categories by Revenue")
    ax.set_xlabel("Revenue (BRL)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"R${x / 1e6:.2f}M"))
    plt.tight_layout()
    return save_figure(fig, "revenue_by_category.png")


def plot_revenue_by_state(df: pd.DataFrame, top_n: int = 10) -> Path:
    require_columns(df, ["revenue"], VIEW_QUERIES["revenue_by_state"])
    state_col = pick_column(
        df, ["customer_state", "state"], VIEW_QUERIES["revenue_by_state"]
    )
    top = df.nlargest(top_n, "revenue").sort_values("revenue")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top[state_col], top["revenue"], color="#3B1F2B")
    ax.set_title(f"Top {top_n} States by Revenue")
    ax.set_xlabel("Revenue (BRL)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"R${x / 1e6:.1f}M"))
    plt.tight_layout()
    return save_figure(fig, "revenue_by_state.png")


def plot_delivery_performance(df: pd.DataFrame) -> Path:
    require_columns(df, ["delay_rate_pct"], VIEW_QUERIES["delivery_performance"])
    period = build_period_column(df, VIEW_QUERIES["delivery_performance"])
    plot_df = df.copy()
    plot_df["period"] = period
    plot_df = plot_df.sort_values("period")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        plot_df["period"],
        plot_df["delay_rate_pct"],
        marker="o",
        linewidth=2,
        color="#C73E1D",
    )
    ax.set_title("Monthly Delivery Delay Rate")
    ax.set_xlabel("Month")
    ax.set_ylabel("Delay Rate (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return save_figure(fig, "delivery_performance.png")


def plot_review_summary(df: pd.DataFrame) -> Path:
    score_col = pick_column(
        df, ["review_score", "score"], VIEW_QUERIES["review_summary"]
    )
    count_col = pick_column(
        df, ["review_count", "count", "reviews"], VIEW_QUERIES["review_summary"]
    )

    plot_df = df.sort_values(score_col)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(plot_df[score_col], plot_df[count_col], color="#2E86AB")
    ax.set_title("Review Score Distribution")
    ax.set_xlabel("Review Score")
    ax.set_ylabel("Review Count")
    plt.tight_layout()
    return save_figure(fig, "review_summary.png")


def plot_repeat_purchase_rate(
    conn: duckdb.DuckDBPyConnection, repeat_df: pd.DataFrame
) -> Path | None:
    """Plot repeat purchase breakdown if the KPI view or fallback query is available."""
    repeat_pct = None
    if not repeat_df.empty:
        pct_col = pick_column(
            repeat_df,
            ["repeat_purchase_rate_pct", "repeat_rate_pct", "repeat_rate"],
            VIEW_QUERIES["repeat_purchase_rate"],
        )
        repeat_pct = float(repeat_df[pct_col].iloc[0])

    try:
        breakdown = conn.execute(REPEAT_BREAKDOWN_SQL).fetchdf()
        require_columns(breakdown, ["order_bucket", "customers"], "repeat breakdown query")
    except Exception as exc:
        print(f"  Skipping repeat purchase chart: {exc}")
        return None

    title = "Customer Order Frequency"
    if repeat_pct is not None:
        title += f" (Repeat Rate: {repeat_pct:.1f}%)"

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(
        breakdown["customers"],
        labels=breakdown["order_bucket"],
        autopct="%1.1f%%",
        colors=["#C73E1D", "#F18F01", "#2E86AB"],
        startangle=90,
    )
    ax.set_title(title)
    plt.tight_layout()
    return save_figure(fig, "repeat_purchase_rate.png")


def export_charts() -> list[Path]:
    """Generate all EDA charts and return saved file paths."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}\n"
            "Run src/data_cleaning.py and src/load_to_database.py first."
        )

    print(f"Database: {DB_PATH}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("Inspecting views...")

    conn = duckdb.connect(str(DB_PATH), read_only=True)
    saved_paths: list[Path] = []

    try:
        revenue_month = inspect_view(conn, VIEW_QUERIES["revenue_trend"])
        revenue_category = inspect_view(conn, VIEW_QUERIES["revenue_by_category"])
        revenue_state = inspect_view(conn, VIEW_QUERIES["revenue_by_state"])
        delivery = inspect_view(conn, VIEW_QUERIES["delivery_performance"])
        reviews = inspect_view(conn, VIEW_QUERIES["review_summary"])

        repeat_df = pd.DataFrame()
        try:
            repeat_df = inspect_view(conn, VIEW_QUERIES["repeat_purchase_rate"])
        except Exception as exc:
            print(f"  Warning: {VIEW_QUERIES['repeat_purchase_rate']} unavailable: {exc}")

        print("\nExporting charts...")
        saved_paths.append(plot_revenue_trend(revenue_month))
        saved_paths.append(plot_revenue_by_category(revenue_category))
        saved_paths.append(plot_revenue_by_state(revenue_state))
        saved_paths.append(plot_delivery_performance(delivery))
        saved_paths.append(plot_review_summary(reviews))

        repeat_path = plot_repeat_purchase_rate(conn, repeat_df)
        if repeat_path is not None:
            saved_paths.append(repeat_path)
    finally:
        conn.close()

    return saved_paths


def main() -> None:
    saved_paths = export_charts()
    print("\nSaved chart files:")
    for path in saved_paths:
        print(f"  {path}")


if __name__ == "__main__":
    main()
