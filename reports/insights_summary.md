# Insights Summary

**Project:** Enterprise Marketing Analytics & Customer 360 Platform  
**Status:** Complete — derived from `olist_analytics.duckdb` and `02_exploratory_analysis.ipynb`  
**Last updated:** 2026-07-03

---

## Purpose

Actionable findings from SQL KPI views and exploratory analysis. All metrics are from delivered orders and live DuckDB views — no fabricated numbers.

---

## Revenue & Growth

### Insight 1: Revenue trends over time
- **Question:** What are the main revenue trends over time?
- **Finding:** Revenue grew from R$40,325 (Oct 2016) to a peak of R$977,545 (May 2018), ending at R$838,577 (Aug 2018). The marketplace scaled rapidly through 2017–2018 with consistent month-over-month growth after early 2017.
- **Evidence:** `kpi_revenue_by_month` — 23 months of data (Sep 2016 – Aug 2018)
- **Action:** Monitor monthly revenue and order count together; investigate any month where orders grow but revenue flatlines (AOV compression).

### Insight 2: Category drivers
- **Question:** Which product categories drive the most revenue?
- **Finding:** Top 5 categories: health_beauty (R$1.23M), watches_gifts (R$1.17M), bed_bath_table (R$1.02M), sports_leisure (R$955K), computers_accessories (R$889K). Top 5 categories account for **39.8%** of total category revenue across 74 categories.
- **Evidence:** `kpi_revenue_by_category`
- **Action:** Prioritize merchandising and marketing spend on top-5 categories; use Pareto view (`vw_category_pareto`) to identify long-tail categories for consolidation.

---

## Customer Behavior

### Insight 3: Segment value
- **Question:** Which customer segments are most valuable?
- **Finding:** Loyal Customers (27,842) generate the most total revenue (R$5.43M), but Champions (5,994) have the highest average CLV (R$273). At Risk and Other segments have low avg CLV (~R$40) despite large counts — retention campaigns should target At Risk (9,773 customers, 431 avg recency days).
- **Evidence:** `vw_segment_summary`, `customer_segments`
- **Action:** Build win-back campaigns for At Risk; VIP program for Champions; nurture Potential Loyalists (23,764 customers, 60 avg recency days) toward second purchase.

### Insight 4: Repeat purchases
- **Question:** What is the repeat purchase rate?
- **Finding:** Only **3.0%** of customers placed 2+ delivered orders. ~97% of customers are one-time buyers in this dataset window — a major retention opportunity.
- **Evidence:** `kpi_repeat_purchase_rate`
- **Action:** Launch post-purchase email flows, loyalty incentives, and measure repeat rate monthly as a north-star retention KPI.

---

## Regional Impact

### Insight 5: Geographic concentration
- **Question:** Which regions have the highest business impact?
- **Finding:** São Paulo (SP) dominates with R$5.07M (38.3% of state revenue), followed by RJ (R$1.76M), MG (R$1.55M), RS (R$729K), PR (R$666K). Top 5 states account for the majority of marketplace revenue.
- **Evidence:** `vw_revenue_by_state`
- **Action:** Optimize logistics and marketing in SP/RJ/MG first; evaluate freight and delivery performance in lower-volume states separately.

---

## Operations & Experience

### Insight 6: Delivery impact on satisfaction
- **Question:** How do delivery performance and review scores affect CX?
- **Finding:** Delivery delay rate is **6.77%** of delivered orders. On-time orders average **4.29** review score vs **2.27** for delayed orders — a 2-point drop. Delayed deliveries are strongly associated with poor customer satisfaction.
- **Evidence:** `vw_delay_vs_review`, `kpi_delivery_delay_rate`, `kpi_avg_review_score` (4.09 overall)
- **Action:** Set operational target to reduce delay rate below 5%; alert sellers/carriers when estimated delivery date is at risk.

### Insight 7: Review distribution
- **Finding:** 57,328 five-star reviews (57.8% of all reviews) vs 11,424 one-star (11.5%). Negative experiences are concentrated among delayed deliveries — fixing logistics should directly improve review scores.
- **Evidence:** `vw_review_summary`

---

## Weekly Executive KPIs

### Insight 8: KPI watchlist
- **Question:** Which KPIs should executives track weekly?

| KPI | Current value | Source view |
|-----|---------------|-------------|
| Total revenue | R$13,221,498 | `kpi_executive_snapshot` |
| Total orders | 96,478 | `kpi_executive_snapshot` |
| Average order value | R$137.04 | `kpi_executive_snapshot` |
| Repeat purchase rate | 3.0% | `kpi_repeat_purchase_rate` |
| Delivery delay rate | 6.77% | `kpi_delivery_delay_rate` |
| Avg review score | 4.09 | `kpi_avg_review_score` |
| Top segment revenue share | Loyal Customers — 41.1% of segment revenue | `vw_segment_summary` |

**Recommended weekly tracking:** revenue, orders, AOV, repeat rate, delay rate, avg review score, top-3 category revenue share.

---

## Deliverables from Phase 3

| Artifact | Location |
|----------|----------|
| EDA notebook | `notebooks/02_exploratory_analysis.ipynb` |
| Chart screenshots | `dashboards/screenshots/` |
| Power BI CSV exports | `data/processed/dashboard_exports/` |
| Executive summary | `reports/executive_summary.md` |
| Weekly KPI report | `reports/weekly_kpi_report.xlsx` |

---

## Next Steps

1. Connect Power BI to `data/processed/dashboard_exports/` or DuckDB directly
2. Build 4 dashboard pages per `docs/dashboard_design_notes.md`
3. Embed chart screenshots in README
4. Phase 2 add-on: Google Analytics + campaign data for attribution analysis
