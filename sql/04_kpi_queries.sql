-- =============================================================================
-- 04_kpi_queries.sql
-- Enterprise Marketing Analytics & Customer 360 Platform
-- Database: DuckDB | Tables: customers, orders, order_items, products, reviews
-- Revenue scope: delivered orders with valid item prices
-- =============================================================================

CREATE OR REPLACE VIEW kpi_total_revenue AS
SELECT
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.is_delivered = 1
  AND oi.is_valid_price = TRUE;

CREATE OR REPLACE VIEW kpi_total_orders AS
SELECT
    COUNT(DISTINCT o.order_id) AS total_orders
FROM orders o
WHERE o.is_delivered = 1;

CREATE OR REPLACE VIEW kpi_total_customers AS
SELECT
    COUNT(DISTINCT c.customer_unique_id) AS total_customers
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.is_delivered = 1;

CREATE OR REPLACE VIEW kpi_average_order_value AS
SELECT
    ROUND(
        (SELECT total_revenue FROM kpi_total_revenue)
        / NULLIF((SELECT total_orders FROM kpi_total_orders), 0),
        2
    ) AS average_order_value;

CREATE OR REPLACE VIEW kpi_repeat_purchase_rate AS
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.is_delivered = 1
    GROUP BY c.customer_unique_id
)
SELECT
    ROUND(
        SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) * 100.0
        / NULLIF(COUNT(*), 0),
        2
    ) AS repeat_purchase_rate_pct
FROM customer_orders;

CREATE OR REPLACE VIEW kpi_revenue_by_month AS
SELECT
    EXTRACT(YEAR FROM CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS year,
    EXTRACT(MONTH FROM CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS month,
    strftime(CAST(o.order_purchase_timestamp AS TIMESTAMP), '%B') AS month_name,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS order_count
FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.is_delivered = 1
  AND oi.is_valid_price = TRUE
GROUP BY 1, 2, 3
ORDER BY year, month;

CREATE OR REPLACE VIEW kpi_revenue_by_category AS
SELECT
    p.category_en,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS order_count
FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.order_id
INNER JOIN products p ON oi.product_id = p.product_id
WHERE o.is_delivered = 1
  AND oi.is_valid_price = TRUE
GROUP BY p.category_en
ORDER BY revenue DESC;

CREATE OR REPLACE VIEW kpi_customer_clv AS
SELECT
    c.customer_unique_id,
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(SUM(oi.price), 2) AS clv
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.is_delivered = 1
  AND oi.is_valid_price = TRUE
GROUP BY c.customer_unique_id, c.customer_state;

CREATE OR REPLACE VIEW kpi_avg_review_score AS
SELECT
    ROUND(AVG(review_score), 2) AS avg_review_score,
    COUNT(*) AS review_count
FROM reviews
WHERE is_valid_score = TRUE;

CREATE OR REPLACE VIEW kpi_delivery_delay_rate AS
SELECT
    ROUND(
        SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0
        / NULLIF(SUM(CASE WHEN is_delivered = 1 THEN 1 ELSE 0 END), 0),
        2
    ) AS delivery_delay_rate_pct,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_orders,
    SUM(CASE WHEN is_delivered = 1 THEN 1 ELSE 0 END) AS delivered_orders
FROM orders;

CREATE OR REPLACE VIEW kpi_executive_snapshot AS
SELECT
    (SELECT total_revenue FROM kpi_total_revenue) AS total_revenue,
    (SELECT total_orders FROM kpi_total_orders) AS total_orders,
    (SELECT total_customers FROM kpi_total_customers) AS total_customers,
    (SELECT average_order_value FROM kpi_average_order_value) AS average_order_value,
    (SELECT repeat_purchase_rate_pct FROM kpi_repeat_purchase_rate) AS repeat_purchase_rate_pct,
    (SELECT avg_review_score FROM kpi_avg_review_score) AS avg_review_score,
    (SELECT delivery_delay_rate_pct FROM kpi_delivery_delay_rate) AS delivery_delay_rate_pct;
