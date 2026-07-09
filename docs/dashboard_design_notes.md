# Dashboard Design Notes — Power BI

**Project:** Enterprise Marketing Analytics & Customer 360 Platform  
**Tool:** Power BI Desktop (primary)  
**Data source:** SQLite / exported views from `sql/06_dashboard_views.sql`  
**Version:** 1.0 — design spec (build in Phase 4)

---

## Design principles

1. **Executive-first** — Page 1 answers "How is the business doing?" in under 10 seconds
2. **Drill-down** — Each page supports filter by date range, state, and category
3. **Consistent KPIs** — Same definitions as `sql/04_kpi_queries.sql` and `docs/data_dictionary.md`
4. **No fake data** — Connect only after processed data and views exist
5. **Portfolio-ready** — Export PNG screenshots to `dashboards/screenshots/` for GitHub README

---

## Global elements (all pages)

| Element | Specification |
|---------|---------------|
| Date slicer | `order_purchase_date` — default: full dataset range |
| State slicer | `customer_state` — multi-select |
| Category slicer | `product_category_en` — multi-select |
| Color palette | Neutral base (grays/white) + one accent (e.g. #2E86AB blue, #A23B72 accent) |
| Font | Segoe UI or Calibri |
| Number format | Revenue: R$ #,##0; Percentages: 0.0%; Scores: 0.00 |

---

## Page 1: Executive Overview

**Audience:** CEO, VP, weekly leadership review  
**Question answered:** How is the business performing overall?

### Layout (wireframe)

```
┌─────────────────────────────────────────────────────────────┐
│  [Date slicer]                              [Logo / Title]  │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Revenue  │ Orders   │ Customers│   AOV    │ Repeat Rate     │
│  (card)  │  (card)  │  (card)  │  (card)  │    (card)       │
├──────────────────────────────┬──────────────────────────────┤
│  Revenue trend (line)        │  Orders by month (column)   │
│  Monthly revenue over time   │  Order volume trend           │
├──────────────────────────────┴──────────────────────────────┤
│  Top 5 categories by revenue (horizontal bar)               │
└─────────────────────────────────────────────────────────────┘
```

### Visuals

| # | Visual type | Field(s) | Purpose |
|---|-------------|----------|---------|
| 1 | Card | total_revenue | Headline revenue KPI |
| 2 | Card | total_orders | Order volume |
| 3 | Card | total_customers | Customer base |
| 4 | Card | average_order_value | Basket size |
| 5 | Card | repeat_purchase_rate | Loyalty signal |
| 6 | Line chart | month, revenue | Revenue trend |
| 7 | Column chart | month, order_count | Volume trend |
| 8 | Bar chart | category_en, revenue | Top categories (Top 5 filter) |

### SQL view

`vw_executive_kpi_summary`, `vw_revenue_by_month`, `vw_revenue_by_category`

---

## Page 2: Customer 360

**Audience:** Marketing, Customer Insights  
**Question answered:** Who are our customers and which segments drive value?

### Layout (wireframe)

```
┌─────────────────────────────────────────────────────────────┐
│  [Date] [State] [Segment slicer]                              │
├──────────────────────────────┬──────────────────────────────┤
│  Segment distribution (donut) │  Revenue by segment (bar)    │
├──────────────────────────────┼──────────────────────────────┤
│  RFM segment matrix (table)   │  CLV distribution (histogram)│
├──────────────────────────────┴──────────────────────────────┤
│  Top 10 customers by CLV (table)                            │
└─────────────────────────────────────────────────────────────┘
```

### Visuals

| # | Visual type | Field(s) | Purpose |
|---|-------------|----------|---------|
| 1 | Donut chart | segment, customer_count | Segment mix |
| 2 | Bar chart | segment, revenue | Value by segment |
| 3 | Table | segment, avg_recency, avg_frequency, avg_monetary, customer_count | RFM detail |
| 4 | Histogram | clv | CLV distribution |
| 5 | Table | customer_unique_id, state, order_count, clv, segment | Top customers |

### Segments (from `05_customer_segmentation.sql`)

Champions, Loyal Customers, Potential Loyalists, At Risk, Lost / Hibernating (adjust labels after scoring).

### SQL view

`vw_customer_segments`, `vw_customer_clv`

---

## Page 3: Revenue & Product Performance

**Audience:** Merchandising, Marketing, Leadership  
**Question answered:** What products and categories drive revenue?

### Layout (wireframe)

```
┌─────────────────────────────────────────────────────────────┐
│  [Date] [Category] [State]                                  │
├──────────────────────────────┬──────────────────────────────┤
│  Revenue by category (bar)    │  Category trend (line)       │
│  Sorted descending            │  Small multiples or top 5    │
├──────────────────────────────┼──────────────────────────────┤
│  Pareto chart (combo)         │  Revenue by state (map/bar)  │
│  Category % of total revenue  │  Geographic performance      │
└──────────────────────────────┴──────────────────────────────┘
```

### Visuals

| # | Visual type | Field(s) | Purpose |
|---|-------------|----------|---------|
| 1 | Bar chart | category_en, revenue | Category ranking |
| 2 | Line chart | month, category_en, revenue | Category trends (Top N) |
| 3 | Combo chart | category_en, revenue, cumulative_pct | Pareto / 80-20 |
| 4 | Filled map or bar | customer_state, revenue | Regional revenue |

### SQL view

`vw_revenue_by_category`, `vw_revenue_by_state`, `vw_category_monthly_trend`

---

## Page 4: Customer Experience & Delivery Performance

**Audience:** Operations, Customer Success, Leadership  
**Question answered:** How does delivery and review quality affect experience?

### Layout (wireframe)

```
┌─────────────────────────────────────────────────────────────┐
│  [Date] [State]                                             │
├──────────┬──────────┬──────────┬──────────────────────────┤
│ Avg      │ Delay    │ Orders   │ Reviews                  │
│ Review   │ Rate     │ w/Review │ Count                    │
│ (card)   │ (card)   │ (card)   │ (card)                   │
├──────────────────────────────┬──────────────────────────────┤
│  Review score distribution    │  Delay rate by month (line)  │
│  (histogram or bar 1-5)       │                              │
├──────────────────────────────┼──────────────────────────────┤
│  Avg review by delay bucket   │  Delay days distribution     │
│  (bar: on-time vs delayed)    │  (histogram)                 │
└──────────────────────────────┴──────────────────────────────┘
```

### Visuals

| # | Visual type | Field(s) | Purpose |
|---|-------------|----------|---------|
| 1 | Card | avg_review_score | CX headline |
| 2 | Card | delivery_delay_rate | Operations headline |
| 3 | Card | orders_with_review | Review coverage |
| 4 | Card | total_reviews | Volume |
| 5 | Bar chart | review_score, count | Score distribution |
| 6 | Line chart | month, delay_rate | Delay trend |
| 7 | Bar chart | delay_bucket, avg_review_score | Delay impact on satisfaction |
| 8 | Histogram | delivery_delay_days | Delay distribution |

### SQL view

`vw_review_summary`, `vw_delivery_performance`, `vw_delay_vs_review`

---

## Tableau (optional)

If building in Tableau, mirror the same 4 pages and field mappings. Store workbook in `dashboards/tableau/`. Use identical KPI definitions for consistency across tools.

---

## Screenshot checklist (for README)

Export at 1920×1080 or 1280×720 PNG:

- [ ] `executive_overview.png`
- [ ] `customer_360.png`
- [ ] `revenue_product.png`
- [ ] `cx_delivery.png`

Save to `dashboards/screenshots/`.

---

## Build order (Phase 4)

1. Connect Power BI to SQLite / exported CSV views
2. Build Page 1 — validate KPI cards against SQL
3. Build Pages 2–4 — add slicers and cross-filtering
4. Format and align visuals
5. Export screenshots
6. Embed screenshots in README

---

## Status

| Item | Status |
|------|--------|
| Design spec | Complete |
| Data connection | Pending (Phase 1) |
| Page 1 build | Not started |
| Page 2 build | Not started |
| Page 3 build | Not started |
| Page 4 build | Not started |
| Screenshots | Not started |
