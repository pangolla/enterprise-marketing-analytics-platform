# EDA Summary

**Project:** Enterprise Marketing Analytics & Customer 360 Platform  
**Data source:** `data/processed/olist_analytics.duckdb`  
**Analysis period:** September 2016 – August 2018 (23 months)  
**Last updated:** 2026-07-06  
**Charts:** `dashboards/screenshots/` (exported via `scripts/export_eda_charts.py`)

All metrics below are from delivered orders and live DuckDB KPI views. No fabricated numbers.

---

## 1. Revenue Trends

**Chart:** `dashboards/screenshots/revenue_trend.png`

The marketplace grew from near-zero volume in late 2016 to sustained monthly revenue above R$800K by 2018.

| Metric | Value |
|--------|-------|
| First recorded month | September 2016 — R$134.97 (1 order) |
| Peak month | November 2017 — R$987,765.37 (7,289 orders) |
| Latest month | August 2018 — R$838,576.64 (6,351 orders) |
| Months in dataset | 23 |

**Key observations:**
- Strong growth through 2017, with revenue accelerating from R$111,798 (Jan 2017) to R$987,765 (Nov 2017).
- 2018 revenue stabilized in the R$826K–R$977K range per month, indicating a mature growth phase.
- Order volume tracked revenue closely — peak month had 7,289 orders vs. 6,351 in the final month.

**Source:** `kpi_revenue_by_month`

---

## 2. Top Product Categories

**Chart:** `dashboards/screenshots/revenue_by_category.png`

| Rank | Category | Revenue (BRL) | Orders |
|------|----------|---------------|--------|
| 1 | health_beauty | 1,233,131.72 | 8,647 |
| 2 | watches_gifts | 1,166,176.98 | 5,495 |
| 3 | bed_bath_table | 1,023,434.76 | 9,272 |
| 4 | sports_leisure | 954,852.55 | 7,530 |
| 5 | computers_accessories | 888,724.61 | 6,530 |

**Key observations:**
- Top 5 categories account for **39.8%** of total category revenue across 74 categories.
- `bed_bath_table` ranks 3rd in revenue but has the highest order count (9,272) among the top 5 — lower AOV than health/beauty or watches.
- Long tail of smaller categories suggests opportunity for assortment optimization.

**Source:** `kpi_revenue_by_category`, `vw_category_pareto`

---

## 3. Customer and Regional Insights

**Charts:** `dashboards/screenshots/revenue_by_state.png`, `dashboards/screenshots/customer_segments.png`

### Regional performance

| State | Revenue (BRL) | Orders | Customers |
|-------|---------------|--------|-----------|
| SP | 5,067,633.16 | 40,501 | 39,156 |
| RJ | 1,759,651.13 | 12,350 | 11,917 |
| MG | 1,552,481.83 | 11,354 | 11,001 |
| RS | 728,897.47 | 5,345 | 5,168 |
| PR | 666,063.51 | 4,923 | 4,769 |

**São Paulo (SP) drives 38.3%** of total state-level revenue. The top 3 states (SP, RJ, MG) dominate marketplace activity.

### Customer segments (RFM)

| Segment | Customers | Avg CLV (BRL) | Total Revenue (BRL) |
|---------|-----------|---------------|---------------------|
| Loyal Customers | 28,403 | 201.63 | 5,726,982.21 |
| Potential Loyalists | 30,461 | 138.27 | 4,211,901.32 |
| Champions | 5,325 | 275.09 | 1,464,840.23 |
| Lost | 6,898 | 135.24 | 932,909.33 |
| At Risk | 12,499 | 40.19 | 502,317.66 |
| Other | 9,810 | 39.00 | 382,547.36 |

**Key observations:**
- **Loyal Customers** generate the most total revenue (R$5.73M, 43.3% of segment revenue).
- **Champions** are the highest-value segment (avg CLV R$275) despite being only 5,325 customers.
- **At Risk** (12,499 customers, 409 avg recency days) and **Other** (low CLV ~R$39) are prime targets for win-back and activation campaigns.

**Sources:** `vw_revenue_by_state`, `vw_segment_summary`, `customer_segments`

---

## 4. Repeat Purchase Rate

**Chart:** `dashboards/screenshots/repeat_purchase_rate.png`

| Metric | Value |
|--------|-------|
| Repeat purchase rate | **3.0%** |
| Customers with 1 order | 90,557 (97.0%) |
| Customers with 2 orders | 2,573 (2.8%) |
| Customers with 3+ orders | 228 (0.2%) |
| Total unique customers | 93,358 |

**Key observations:**
- The vast majority of customers (97%) made only one delivered purchase in the observation window.
- Repeat behavior is a major growth lever — even a 2-point increase in repeat rate would add ~1,870 returning customers.
- Potential Loyalists (30,461 customers, 101 avg recency days) are the best near-term retention target.

**Source:** `kpi_repeat_purchase_rate`, `customer_segments`

---

## 5. Delivery Performance and Review Scores

**Charts:** `dashboards/screenshots/delivery_performance.png`, `dashboards/screenshots/review_summary.png`

### Delivery performance

| Metric | Value |
|--------|-------|
| Delivery delay rate | **6.77%** |
| Delayed orders | 6,532 |
| Delivered orders | 96,478 |
| Avg monthly delay rate | 9.5% |
| Min / max monthly delay rate | 0.0% / 100.0% |

### Review scores

| Metric | Value |
|--------|-------|
| Overall avg review score | **4.09** (scale 1–5) |
| Total reviews | 99,224 |
| 5-star reviews | 57,328 (57.8%) |
| 1-star reviews | 11,424 (11.5%) |

### Delivery impact on satisfaction

| Delivery status | Avg review score | Reviews |
|-----------------|------------------|---------|
| On Time | **4.29** | 89,952 |
| Delayed | **2.27** | 6,409 |

**Key observations:**
- Delayed deliveries score **2.02 points lower** on average than on-time orders — a strong causal signal for operations investment.
- 57.8% of reviews are 5-star, but the delayed subset pulls the overall average down.
- Reducing the 6.77% delay rate should directly improve customer satisfaction and repeat purchase potential.

**Sources:** `kpi_delivery_delay_rate`, `vw_delivery_performance`, `vw_review_summary`, `vw_delay_vs_review`, `kpi_avg_review_score`

---

## 6. Executive KPIs

**Chart:** `dashboards/screenshots/revenue_trend.png` (overview context)

| KPI | Value | Source view |
|-----|-------|-------------|
| Total revenue | R$13,221,498.11 | `kpi_executive_snapshot` |
| Total orders (delivered) | 96,478 | `kpi_executive_snapshot` |
| Total customers | 93,358 | `kpi_executive_snapshot` |
| Average order value | R$137.04 | `kpi_executive_snapshot` |
| Repeat purchase rate | 3.0% | `kpi_executive_snapshot` |
| Avg review score | 4.09 | `kpi_executive_snapshot` |
| Delivery delay rate | 6.77% | `kpi_executive_snapshot` |

### Weekly executive watchlist

1. **Total revenue** — monthly trend and WoW change
2. **Total orders** — volume health indicator
3. **Average order value** — basket size monitoring
4. **Repeat purchase rate** — retention north-star (currently 3.0%)
5. **Delivery delay rate** — operations quality (currently 6.77%)
6. **Avg review score** — customer experience pulse (currently 4.09)
7. **Top-3 category revenue share** — merchandising concentration risk

---

## 7. Business Recommendations

### Revenue growth
- **Invest in top categories** (health_beauty, watches_gifts, bed_bath_table) which drive 39.8% of revenue.
- **Monitor AOV by category** — bed_bath_table has high volume but lower revenue per order; bundle or upsell strategies could lift AOV.
- **Chart reference:** `revenue_by_category.png`, `revenue_trend.png`

### Customer retention
- **Launch retention campaigns** targeting the 97% single-purchase customers — even modest improvement in the 3.0% repeat rate has outsized revenue impact.
- **Nurture Potential Loyalists** (30,461 customers, recent activity) with second-purchase incentives.
- **Protect Champions** (5,325 customers, R$275 avg CLV) with VIP treatment and early access.
- **Chart reference:** `repeat_purchase_rate.png`

### Regional strategy
- **Prioritize SP, RJ, MG** for logistics, marketing, and seller onboarding — they account for the majority of revenue.
- **Evaluate delivery performance separately** in lower-volume states before expanding marketing spend.
- **Chart reference:** `revenue_by_state.png`

### Operations and customer experience
- **Set a delay rate target below 5%** (current: 6.77%) — delayed orders average 2.27 vs. 4.29 for on-time.
- **Alert sellers** when orders approach estimated delivery date without carrier handoff.
- **Track monthly delay trend** to catch operational regressions early.
- **Chart reference:** `delivery_performance.png`, `review_summary.png`

### Win-back and risk mitigation
- **At Risk segment** (12,499 customers, 409 avg recency days, R$40 avg CLV) — deploy win-back email/promo campaigns.
- **Lost segment** (6,898 customers) — test reactivation offers with controlled budget.
- **Chart reference:** `customer_segments.png`

---

## Exported chart inventory

| File | Description |
|------|-------------|
| `dashboards/screenshots/revenue_trend.png` | Monthly revenue line chart |
| `dashboards/screenshots/revenue_by_category.png` | Top 10 categories horizontal bar chart |
| `dashboards/screenshots/revenue_by_state.png` | Top 10 states horizontal bar chart |
| `dashboards/screenshots/delivery_performance.png` | Monthly delay rate trend |
| `dashboards/screenshots/review_summary.png` | Review score distribution bar chart |
| `dashboards/screenshots/repeat_purchase_rate.png` | Customer order frequency pie chart |

**Regenerate charts:** `python scripts/export_eda_charts.py`

---

## Related documentation

| Document | Purpose |
|----------|---------|
| `docs/data_dictionary.md` | Table and KPI definitions |
| `docs/dashboard_design_notes.md` | Power BI page specifications |
| `reports/insights_summary.md` | Actionable insights for stakeholders |
| `reports/executive_summary.md` | Auto-generated executive narrative |

---

_Analysis based on Olist Brazilian E-Commerce public dataset. Metrics reflect delivered orders only._
