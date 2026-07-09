-- =============================================================================
-- 06_dashboard_views.sql
-- Enterprise Marketing Analytics & Customer 360 Platform
-- Denormalized views for Power BI / Excel (see docs/dashboard_design_notes.md)
-- =============================================================================

-- Page 1: Executive Overview
CREATE OR REPLACE VIEW vw_executive_kpi_summary AS
SELECT * FROM kpi_executive_snapshot;

CREATE OR REPLACE VIEW vw_revenue_by_month AS
SELECT * FROM kpi_revenue_by_month;

CREATE OR REPLACE VIEW vw_revenue_by_category AS
SELECT * FROM kpi_revenue_by_category;

-- Page 2: Customer 360
CREATE OR REPLACE VIEW vw_customer_segments AS
SELECT * FROM customer_segments;

CREATE OR REPLACE VIEW vw_customer_clv AS
SELECT * FROM kpi_customer_clv;

-- Page 3: Revenue & Product Performance
CREATE OR REPLACE VIEW vw_revenue_by_state AS
SELECT
    c.customer_state,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(DISTINCT c.customer_unique_id) AS customer_count
FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.order_id
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE o.is_delivered = 1
  AND oi.is_valid_price = TRUE
GROUP BY c.customer_state
ORDER BY revenue DESC;

CREATE OR REPLACE VIEW vw_category_monthly_trend AS
SELECT
    EXTRACT(YEAR FROM CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS year,
    EXTRACT(MONTH FROM CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS month,
    strftime(CAST(o.order_purchase_timestamp AS TIMESTAMP), '%B') AS month_name,
    p.category_en,
    ROUND(SUM(oi.price), 2) AS revenue
FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.order_id
INNER JOIN products p ON oi.product_id = p.product_id
WHERE o.is_delivered = 1
  AND oi.is_valid_price = TRUE
GROUP BY 1, 2, 3, 4
ORDER BY year, month, revenue DESC;

CREATE OR REPLACE VIEW vw_category_pareto AS
WITH category_rev AS (
    SELECT category_en, revenue
    FROM kpi_revenue_by_category
),
ranked AS (
    SELECT
        category_en,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue,
        SUM(revenue) OVER () AS total_revenue
    FROM category_rev
)
SELECT
    category_en,
    revenue,
    ROUND(cumulative_revenue * 100.0 / total_revenue, 2) AS cumulative_pct
FROM ranked
ORDER BY revenue DESC;

-- Page 4: Customer Experience & Delivery
CREATE OR REPLACE VIEW vw_review_summary AS
SELECT
    review_score,
    COUNT(*) AS review_count
FROM reviews
WHERE is_valid_score = TRUE
GROUP BY review_score
ORDER BY review_score;

CREATE OR REPLACE VIEW vw_delivery_performance AS
SELECT
    EXTRACT(YEAR FROM CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS year,
    EXTRACT(MONTH FROM CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS month,
    strftime(CAST(o.order_purchase_timestamp AS TIMESTAMP), '%B') AS month_name,
    COUNT(*) AS delivered_orders,
    SUM(o.is_delayed) AS delayed_orders,
    ROUND(SUM(o.is_delayed) * 100.0 / NULLIF(COUNT(*), 0), 2) AS delay_rate_pct
FROM orders o
WHERE o.is_delivered = 1
GROUP BY 1, 2, 3
ORDER BY year, month;

CREATE OR REPLACE VIEW vw_delay_vs_review AS
SELECT
    CASE
        WHEN o.is_delayed = 1 THEN 'Delayed'
        WHEN o.is_delayed = 0 THEN 'On Time'
        ELSE 'Unknown'
    END AS delay_bucket,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    COUNT(*) AS review_count
FROM orders o
INNER JOIN reviews r ON o.order_id = r.order_id
WHERE o.is_delivered = 1
  AND r.is_valid_score = TRUE
GROUP BY 1;

CREATE OR REPLACE VIEW vw_delivery_delay_distribution AS
SELECT
    o.delivery_delay_days,
    COUNT(*) AS order_count
FROM orders o
WHERE o.is_delivered = 1
  AND o.delivery_delay_days IS NOT NULL
GROUP BY o.delivery_delay_days
ORDER BY o.delivery_delay_days;
