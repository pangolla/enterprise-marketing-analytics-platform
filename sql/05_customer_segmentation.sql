-- =============================================================================
-- 05_customer_segmentation.sql
-- Enterprise Marketing Analytics & Customer 360 Platform
-- Method: RFM (Recency, Frequency, Monetary) with DuckDB NTILE quintiles
-- =============================================================================

CREATE OR REPLACE TABLE customer_rfm AS
SELECT
    c.customer_unique_id,
    c.customer_state,
    CAST(
        DATE_DIFF(
            'day',
            MAX(CAST(o.order_purchase_timestamp AS TIMESTAMP)),
            (SELECT MAX(CAST(order_purchase_timestamp AS TIMESTAMP)) FROM orders WHERE is_delivered = 1)
        ) AS INTEGER
    ) AS recency_days,
    COUNT(DISTINCT o.order_id) AS frequency,
    ROUND(SUM(oi.price), 2) AS monetary
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.is_delivered = 1
  AND oi.is_valid_price = TRUE
GROUP BY c.customer_unique_id, c.customer_state;

CREATE OR REPLACE TABLE customer_rfm_scored AS
SELECT
    customer_unique_id,
    customer_state,
    recency_days,
    frequency,
    monetary,
    6 - NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
FROM customer_rfm;

CREATE OR REPLACE VIEW customer_segments AS
SELECT
    customer_unique_id,
    customer_state,
    recency_days,
    frequency,
    monetary,
    monetary AS clv,
    r_score,
    f_score,
    m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 3 AND f_score <= 2 THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Other'
    END AS segment_name
FROM customer_rfm_scored;

CREATE OR REPLACE VIEW kpi_revenue_by_segment AS
SELECT
    segment_name,
    COUNT(DISTINCT customer_unique_id) AS customer_count,
    ROUND(SUM(clv), 2) AS segment_revenue,
    ROUND(AVG(clv), 2) AS avg_clv
FROM customer_segments
GROUP BY segment_name
ORDER BY segment_revenue DESC;

CREATE OR REPLACE VIEW vw_segment_summary AS
SELECT
    segment_name,
    COUNT(*) AS customer_count,
    ROUND(AVG(monetary), 2) AS avg_clv,
    ROUND(SUM(monetary), 2) AS total_revenue,
    ROUND(AVG(frequency), 1) AS avg_frequency,
    ROUND(AVG(recency_days), 0) AS avg_recency_days
FROM customer_segments
GROUP BY segment_name
ORDER BY total_revenue DESC;
