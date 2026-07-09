# Data Dictionary

**Project:** Enterprise Marketing Analytics & Customer 360 Platform  
**Source:** Olist Brazilian E-Commerce Public Dataset (Kaggle)  
**Version:** 1.0 — Olist only  
**Last updated:** Phase 0 (structure)

---

## Overview

This document defines source tables, target analytics schema, and KPI field definitions. Update this file as cleaning rules and derived fields are finalized in Phase 1.

---

## Source Tables (`data/raw/`)

### olist_orders

Order-level transactional data.

| Column | Type | Description |
|--------|------|-------------|
| order_id | string | Unique order identifier |
| customer_id | string | FK to olist_customers |
| order_status | string | e.g. delivered, shipped, canceled |
| order_purchase_timestamp | datetime | When the order was placed |
| order_approved_at | datetime | Payment approval timestamp |
| order_delivered_carrier_date | datetime | Handoff to carrier |
| order_delivered_customer_date | datetime | Actual delivery to customer |
| order_estimated_delivery_date | datetime | Promised delivery date |

**Grain:** One row per order.

---

### olist_order_items

Line-item detail for each order.

| Column | Type | Description |
|--------|------|-------------|
| order_id | string | FK to olist_orders |
| order_item_id | integer | Line item sequence within order |
| product_id | string | FK to olist_products |
| seller_id | string | FK to olist_sellers |
| shipping_limit_date | datetime | Seller shipping deadline |
| price | float | Item price (BRL) |
| freight_value | float | Shipping cost for this item (BRL) |

**Grain:** One row per order line item.

---

### olist_products

Product master data.

| Column | Type | Description |
|--------|------|-------------|
| product_id | string | Unique product identifier |
| product_category_name | string | Category (Portuguese) |
| product_name_lenght | integer | Name character length |
| product_description_lenght | integer | Description character length |
| product_photos_qty | integer | Number of product photos |
| product_weight_g | float | Weight in grams |
| product_length_cm | float | Length in cm |
| product_height_cm | float | Height in cm |
| product_width_cm | float | Width in cm |

**Grain:** One row per product.

---

### product_category_name_translation

English translation for product categories.

| Column | Type | Description |
|--------|------|-------------|
| product_category_name | string | Category name (Portuguese) |
| product_category_name_english | string | Category name (English) |

---

### olist_customers

Customer geographic attributes.

| Column | Type | Description |
|--------|------|-------------|
| customer_id | string | Unique customer identifier |
| customer_unique_id | string | Stable customer ID across orders |
| customer_zip_code_prefix | string | ZIP code prefix |
| customer_city | string | City |
| customer_state | string | Brazilian state code (2 letters) |

**Grain:** One row per customer_id (note: customer_unique_id is the true customer key for CLV).

---

### olist_order_reviews

Post-purchase review data.

| Column | Type | Description |
|--------|------|-------------|
| review_id | string | Unique review identifier |
| order_id | string | FK to olist_orders |
| review_score | integer | Score 1–5 |
| review_comment_title | string | Optional review title |
| review_comment_message | string | Optional review text |
| review_creation_date | datetime | When review was created |
| review_answer_timestamp | datetime | When seller responded |

**Grain:** One row per review.

---

### olist_order_payments

Payment details per order (optional for V1 KPIs).

| Column | Type | Description |
|--------|------|-------------|
| order_id | string | FK to olist_orders |
| payment_sequential | integer | Payment sequence number |
| payment_type | string | e.g. credit_card, boleto, voucher |
| payment_installments | integer | Number of installments |
| payment_value | float | Payment amount (BRL) |

**Grain:** One row per payment record per order.

---

## Target Analytics Schema (SQL)

Defined in `sql/01_create_tables.sql`. Summary:

| Table | Type | Grain | Key fields |
|-------|------|-------|------------|
| dim_customer | Dimension | customer_unique_id | city, state, zip |
| dim_product | Dimension | product_id | category_en, weight, dimensions |
| dim_date | Dimension | date | year, month, quarter |
| fact_orders | Fact | order_id | customer_key, dates, status, delay_flag |
| fact_order_items | Fact | order_id + item_id | product_key, price, freight |
| fact_reviews | Fact | review_id | order_key, review_score |

---

## Derived Fields (cleaning layer)

| Field | Definition | Source |
|-------|------------|--------|
| order_revenue | Sum of `price` per order | fact_order_items |
| is_delivered | order_status = 'delivered' | fact_orders |
| delivery_delay_days | delivered_date − estimated_date (days) | fact_orders |
| is_delayed | delivery_delay_days > 0 | fact_orders |
| product_category_en | English category name | dim_product |
| customer_order_count | Orders per customer_unique_id | aggregation |
| clv | Total revenue per customer_unique_id | aggregation |

---

## KPI Definitions

| KPI | Formula | Notes |
|-----|---------|-------|
| Total revenue | SUM(price) WHERE is_delivered | Excludes canceled orders |
| Total orders | COUNT(DISTINCT order_id) WHERE is_delivered | |
| Total customers | COUNT(DISTINCT customer_unique_id) | |
| AOV | total_revenue / total_orders | |
| Repeat purchase rate | customers with 2+ orders / total customers | |
| Revenue by month | SUM(price) GROUP BY year-month | |
| Revenue by category | SUM(price) GROUP BY category_en | |
| CLV | SUM(price) per customer_unique_id | Simple historical CLV |
| Avg review score | AVG(review_score) | Scale 1–5 |
| Delivery delay rate | COUNT(delayed) / COUNT(delivered) | |

---

## Data Quality Notes (to validate in Phase 1)

- [ ] Confirm `customer_id` vs `customer_unique_id` usage for customer metrics
- [ ] Handle orders without reviews (left join, not inner)
- [ ] Filter canceled / unavailable orders for revenue KPIs
- [ ] Parse all timestamp columns to consistent datetime format
- [ ] Join category translation for English labels

---

## Planned Additions (Version 2)

- Google Analytics events and session tables
- Marketing campaign spend and attribution fields
