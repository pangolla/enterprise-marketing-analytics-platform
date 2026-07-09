"""
data_cleaning.py
Enterprise Marketing Analytics & Customer 360 Platform

Purpose: Load Olist raw CSVs, clean and standardize fields, export processed files.

Usage:
    python src/data_cleaning.py
"""

from pathlib import Path

import pandas as pd

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
    "payments": "olist_order_payments_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
}


def load_raw(filename: str) -> pd.DataFrame:
    """Load a single CSV from data/raw/. Raises FileNotFoundError if missing."""
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing raw file: {path}\n"
            "Download Olist CSVs from Kaggle and place them in data/raw/"
        )
    return pd.read_csv(path, low_memory=False)


def parse_datetime_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Parse specified columns to datetime. Invalid values become NaT."""
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean orders table.
    - Parse timestamps
    - Standardize order_status
    - Compute delivery delay metrics for delivered orders
    """
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    df = parse_datetime_columns(df, date_cols)
    df["order_status"] = df["order_status"].astype(str).str.strip().str.lower()

    df["is_delivered"] = (df["order_status"] == "delivered").astype(int)

    delivered_mask = df["is_delivered"] == 1
    df["delivery_delay_days"] = pd.NA
    df.loc[delivered_mask, "delivery_delay_days"] = (
        df.loc[delivered_mask, "order_delivered_customer_date"]
        - df.loc[delivered_mask, "order_estimated_delivery_date"]
    ).dt.days

    df["is_delayed"] = 0
    df.loc[delivered_mask, "is_delayed"] = (
        df.loc[delivered_mask, "delivery_delay_days"] > 0
    ).astype(int)

    df["purchase_date"] = df["order_purchase_timestamp"].dt.date

    return df


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Clean order items — cast numerics and flag invalid prices."""
    df = df.copy()
    df = parse_datetime_columns(df, ["shipping_limit_date"])

    for col in ("price", "freight_value"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Keep invalid rows for audit; revenue KPIs filter on joined delivered orders
    df["is_valid_price"] = (df["price"].notna()) & (df["price"] >= 0)
    df["is_valid_freight"] = (df["freight_value"].notna()) & (df["freight_value"] >= 0)

    return df


def clean_products(df: pd.DataFrame, category_translation: pd.DataFrame) -> pd.DataFrame:
    """Clean products and join English category names."""
    df = df.copy()
    translation = category_translation.copy()
    translation.columns = [c.strip() for c in translation.columns]

    df = df.merge(
        translation,
        on="product_category_name",
        how="left",
    )
    df["category_en"] = df["product_category_name_english"].fillna(
        df["product_category_name"]
    )
    df["category_en"] = df["category_en"].fillna("Unknown")

    numeric_cols = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean customer table — standardize text fields."""
    df = df.copy()
    df["customer_city"] = df["customer_city"].astype(str).str.strip().str.title()
    df["customer_state"] = df["customer_state"].astype(str).str.strip().str.upper()
    df["customer_zip_code_prefix"] = (
        df["customer_zip_code_prefix"].astype(str).str.strip()
    )
    return df


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Clean reviews — validate review_score range 1-5 and parse dates."""
    df = df.copy()
    df = parse_datetime_columns(df, ["review_creation_date", "review_answer_timestamp"])

    df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce")
    df["is_valid_score"] = df["review_score"].between(1, 5)

    return df


def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    """Clean payment records — cast numerics."""
    df = df.copy()
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce")
    df["payment_installments"] = pd.to_numeric(
        df["payment_installments"], errors="coerce"
    )
    return df


def build_data_quality_report(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Summarize row counts and key quality metrics per table."""
    rows = []

    orders = tables["orders"]
    rows.append({"table": "orders", "metric": "row_count", "value": len(orders)})
    rows.append({
        "table": "orders",
        "metric": "delivered_pct",
        "value": round(orders["is_delivered"].mean() * 100, 2),
    })
    rows.append({
        "table": "orders",
        "metric": "delayed_among_delivered_pct",
        "value": round(
            orders.loc[orders["is_delivered"] == 1, "is_delayed"].mean() * 100, 2
        ),
    })

    items = tables["order_items"]
    rows.append({"table": "order_items", "metric": "row_count", "value": len(items)})
    rows.append({
        "table": "order_items",
        "metric": "invalid_price_count",
        "value": int((~items["is_valid_price"]).sum()),
    })

    products = tables["products"]
    rows.append({"table": "products", "metric": "row_count", "value": len(products)})
    rows.append({
        "table": "products",
        "metric": "unknown_category_pct",
        "value": round((products["category_en"] == "Unknown").mean() * 100, 2),
    })

    customers = tables["customers"]
    rows.append({"table": "customers", "metric": "row_count", "value": len(customers)})
    rows.append({
        "table": "customers",
        "metric": "unique_customers",
        "value": customers["customer_unique_id"].nunique(),
    })

    reviews = tables["reviews"]
    rows.append({"table": "reviews", "metric": "row_count", "value": len(reviews)})
    rows.append({
        "table": "reviews",
        "metric": "invalid_score_count",
        "value": int((~reviews["is_valid_score"]).sum()),
    })

    return pd.DataFrame(rows)


def export_processed(tables: dict[str, pd.DataFrame]) -> None:
    """Write cleaned tables to data/processed/ as CSV."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        csv_path = PROCESSED_DIR / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        print(f"Exported: {csv_path} ({len(df):,} rows)")


def run_cleaning_pipeline() -> dict[str, pd.DataFrame]:
    """Main cleaning pipeline. Returns dict of cleaned DataFrames."""
    print("Loading raw Olist files from data/raw/ ...")

    orders = clean_orders(load_raw(RAW_FILES["orders"]))
    order_items = clean_order_items(load_raw(RAW_FILES["order_items"]))
    products = clean_products(
        load_raw(RAW_FILES["products"]),
        load_raw(RAW_FILES["category_translation"]),
    )
    customers = clean_customers(load_raw(RAW_FILES["customers"]))
    reviews = clean_reviews(load_raw(RAW_FILES["reviews"]))
    payments = clean_payments(load_raw(RAW_FILES["payments"]))

    tables = {
        "orders": orders,
        "order_items": order_items,
        "products": products,
        "customers": customers,
        "reviews": reviews,
        "payments": payments,
    }

    quality = build_data_quality_report(tables)
    tables["data_quality_report"] = quality

    export_processed(tables)

    print("\nData quality summary:")
    print(quality.to_string(index=False))

    return tables


if __name__ == "__main__":
    run_cleaning_pipeline()
