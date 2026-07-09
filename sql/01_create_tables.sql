-- =============================================================================
-- 01_create_tables.sql
-- Enterprise Marketing Analytics & Customer 360 Platform
-- =============================================================================
-- Purpose: Define star-schema tables for Olist e-commerce analytics.
-- Database: SQLite (portfolio) — adapt syntax for PostgreSQL/BigQuery as needed.
-- Status:  PLACEHOLDER — run after downloading Olist CSVs to data/raw/
-- Order:    Run this file FIRST before 02_load_data.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Dimension: Customer
-- Grain: one row per customer_unique_id (stable customer key)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_unique_id    TEXT    NOT NULL UNIQUE,
    customer_zip_prefix   TEXT,
    customer_city         TEXT,
    customer_state        TEXT,
    created_at            TEXT    DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------------------------
-- Dimension: Product
-- Grain: one row per product_id
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_product (
    product_key           INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id            TEXT    NOT NULL UNIQUE,
    category_pt           TEXT,
    category_en           TEXT,
    weight_g              REAL,
    length_cm             REAL,
    height_cm             REAL,
    width_cm              REAL,
    created_at            TEXT    DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------------------------
-- Dimension: Date
-- Grain: one row per calendar date
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_key              INTEGER PRIMARY KEY,  -- YYYYMMDD format
    full_date             TEXT    NOT NULL UNIQUE,
    year                  INTEGER,
    quarter               INTEGER,
    month                 INTEGER,
    month_name            TEXT,
    day_of_week           INTEGER,
    is_weekend            INTEGER
);

-- -----------------------------------------------------------------------------
-- Fact: Orders
-- Grain: one row per order_id
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_orders (
    order_key                     INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id                      TEXT    NOT NULL UNIQUE,
    customer_key                  INTEGER REFERENCES dim_customer(customer_key),
    purchase_date_key             INTEGER REFERENCES dim_date(date_key),
    order_status                  TEXT,
    order_purchase_timestamp      TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT,
    is_delivered                  INTEGER DEFAULT 0,  -- 1 = delivered
    delivery_delay_days           REAL,
    is_delayed                    INTEGER DEFAULT 0,  -- 1 = delivered after estimate
    created_at                    TEXT    DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------------------------
-- Fact: Order Items
-- Grain: one row per order_id + order_item_id
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_order_items (
    order_item_key        INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id              TEXT    NOT NULL,
    order_item_id         INTEGER NOT NULL,
    order_key             INTEGER REFERENCES fact_orders(order_key),
    product_key           INTEGER REFERENCES dim_product(product_key),
    seller_id             TEXT,
    price                 REAL,
    freight_value         REAL,
    created_at            TEXT    DEFAULT (datetime('now')),
    UNIQUE (order_id, order_item_id)
);

-- -----------------------------------------------------------------------------
-- Fact: Reviews
-- Grain: one row per review_id
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_reviews (
    review_key            INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id             TEXT    NOT NULL UNIQUE,
    order_key             INTEGER REFERENCES fact_orders(order_key),
    order_id              TEXT,
    review_score          INTEGER,
    review_creation_date  TEXT,
    created_at            TEXT    DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------------------------
-- Staging tables (temporary — populated before fact/dim load)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stg_orders          (LIKE fact_orders);          -- SQLite: copy structure manually if LIKE unsupported
CREATE TABLE IF NOT EXISTS stg_order_items     (LIKE fact_order_items);
CREATE TABLE IF NOT EXISTS stg_customers       (LIKE dim_customer);
CREATE TABLE IF NOT EXISTS stg_products        (LIKE dim_product);
CREATE TABLE IF NOT EXISTS stg_reviews         (LIKE fact_reviews);

-- NOTE: SQLite does not support CREATE TABLE LIKE in all versions.
-- If staging fails, create stg_* tables with explicit column definitions
-- matching the raw CSV structure. See 02_load_data.sql.

-- -----------------------------------------------------------------------------
-- Indexes (add after data load for performance)
-- -----------------------------------------------------------------------------
-- CREATE INDEX IF NOT EXISTS idx_fact_orders_customer    ON fact_orders(customer_key);
-- CREATE INDEX IF NOT EXISTS idx_fact_orders_purchase    ON fact_orders(purchase_date_key);
-- CREATE INDEX IF NOT EXISTS idx_fact_items_order        ON fact_order_items(order_key);
-- CREATE INDEX IF NOT EXISTS idx_fact_items_product      ON fact_order_items(product_key);
-- CREATE INDEX IF NOT EXISTS idx_fact_reviews_order      ON fact_reviews(order_key);

-- PLACEHOLDER: Uncomment indexes after successful data load in Phase 1.
