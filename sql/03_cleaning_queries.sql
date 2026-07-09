-- =============================================================================
-- 03_cleaning_queries.sql
-- Enterprise Marketing Analytics & Customer 360 Platform
-- =============================================================================
-- Purpose: Standardize, validate, and enrich loaded data.
-- Status:  PLACEHOLDER — run after 02_load_data.sql
-- Order:    Run AFTER data load, BEFORE KPI queries
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Standardize order status values
-- -----------------------------------------------------------------------------
-- UPDATE fact_orders
-- SET order_status = LOWER(TRIM(order_status))
-- WHERE order_status IS NOT NULL;

-- -----------------------------------------------------------------------------
-- 2. Flag delivered orders and compute delivery delay
-- -----------------------------------------------------------------------------
-- UPDATE fact_orders
-- SET
--     is_delivered = CASE WHEN order_status = 'delivered' THEN 1 ELSE 0 END,
--     delivery_delay_days = CASE
--         WHEN order_status = 'delivered'
--              AND order_delivered_customer_date IS NOT NULL
--              AND order_estimated_delivery_date IS NOT NULL
--         THEN julianday(order_delivered_customer_date) - julianday(order_estimated_delivery_date)
--         ELSE NULL
--     END;

-- UPDATE fact_orders
-- SET is_delayed = CASE WHEN delivery_delay_days > 0 THEN 1 ELSE 0 END
-- WHERE is_delivered = 1;

-- -----------------------------------------------------------------------------
-- 3. Remove or flag invalid prices
-- -----------------------------------------------------------------------------
-- SELECT order_id, order_item_id, price
-- FROM fact_order_items
-- WHERE price IS NULL OR price < 0;
-- PLACEHOLDER: Decide handling (exclude from revenue KPIs vs. impute)

-- -----------------------------------------------------------------------------
-- 4. Fill missing English categories
-- -----------------------------------------------------------------------------
-- UPDATE dim_product
-- SET category_en = COALESCE(category_en, category_pt, 'Unknown')
-- WHERE category_en IS NULL OR category_en = '';

-- -----------------------------------------------------------------------------
-- 5. Deduplicate reviews (if any)
-- -----------------------------------------------------------------------------
-- DELETE FROM fact_reviews
-- WHERE review_key NOT IN (
--     SELECT MIN(review_key)
--     FROM fact_reviews
--     GROUP BY review_id
-- );

-- -----------------------------------------------------------------------------
-- 6. Data quality summary (run and document results in Phase 1)
-- -----------------------------------------------------------------------------
-- SELECT
--     'orders_missing_customer' AS check_name,
--     COUNT(*) AS issue_count
-- FROM fact_orders
-- WHERE customer_key IS NULL

-- UNION ALL

-- SELECT
--     'items_missing_product',
--     COUNT(*)
-- FROM fact_order_items
-- WHERE product_key IS NULL

-- UNION ALL

-- SELECT
--     'delivered_orders_no_delivery_date',
--     COUNT(*)
-- FROM fact_orders
-- WHERE is_delivered = 1 AND order_delivered_customer_date IS NULL;

-- PLACEHOLDER: Record quality check results in docs/data_dictionary.md
