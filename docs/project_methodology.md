# Project Methodology

**Project:** Enterprise Marketing Analytics & Customer 360 Platform  
**Approach:** CRISP-DM adapted for portfolio analytics engineering  
**Version:** 1.0

---

## 1. Business Understanding

### Objective

Build a Customer 360 analytics platform that enables leadership and marketing teams to monitor revenue, segment customers, and improve post-purchase experience.

### Stakeholders (simulated)

| Stakeholder | Need |
|-------------|------|
| CEO / VP | Weekly KPI scorecard, revenue trends |
| Marketing | Customer segments, repeat behavior, category performance |
| Operations | Delivery delay rate, review scores |
| Analytics team | Reproducible SQL layer, automated reporting |

### Success criteria

- All 7 business questions answerable from SQL + dashboards
- Pipeline reproducible from raw CSV to executive report
- Documentation sufficient for a recruiter to evaluate without a live walkthrough

---

## 2. Data Understanding

### Source

Olist Brazilian E-Commerce — ~100k orders, multiple related tables (2016–2018).

### Exploration plan (`notebooks/02_exploratory_analysis.ipynb`)

1. Row counts and primary keys per table
2. Null rates on critical fields (dates, prices, categories)
3. Order status distribution
4. Revenue concentration by category and state
5. Review score distribution
6. Delivery delay distribution

### Known considerations

- `customer_id` changes per order; use `customer_unique_id` for customer-level metrics
- Not all orders have reviews
- Category names are in Portuguese until translation join

---

## 3. Data Preparation

### Python cleaning (`src/data_cleaning.py`, `notebooks/01_data_cleaning.ipynb`)

| Step | Action |
|------|--------|
| Load | Read CSVs from `data/raw/` |
| Type cast | Parse timestamps, numeric prices |
| Filter | Flag delivered vs. canceled orders |
| Enrich | Join category translation; compute delay days |
| Validate | Assert no negative prices; log null rates |
| Export | Write cleaned tables to `data/processed/` |

### SQL cleaning (`sql/03_cleaning_queries.sql`)

- Standardize status values
- Deduplicate staging loads
- Populate `dim_*` and `fact_*` tables
- Create indexes on join keys

---

## 4. Data Modeling

### Schema pattern: Star schema

```
dim_customer ──┐
dim_product  ──┼── fact_order_items ── fact_orders ── dim_date
               └── fact_reviews
```

### Segmentation methodology

**RFM (Recency, Frequency, Monetary)** on `customer_unique_id`:

| Dimension | Definition |
|-----------|------------|
| Recency | Days since last order |
| Frequency | Total order count |
| Monetary | Total revenue |

Segments (e.g., Champions, Loyal, At Risk, Lost) assigned via quintile scoring in `sql/05_customer_segmentation.sql`.

---

## 5. Analysis & KPI Layer

### SQL-first analytics

All KPIs defined as views in `sql/04_kpi_queries.sql` and exposed to Power BI via `sql/06_dashboard_views.sql`.

### Notebook analysis

- `03_customer_segmentation.ipynb` — RFM validation, segment profiles
- `04_campaign_analysis.ipynb` — Placeholder for Version 2 campaign data

---

## 6. Deployment & Delivery

### Artifacts

| Artifact | Tool | Location |
|----------|------|----------|
| Analytics database | SQLite | `data/processed/olist_analytics.db` |
| Power BI dashboard | Power BI Desktop | `dashboards/powerbi/` |
| Weekly KPI report | Python + Excel | `reports/weekly_kpi_report.xlsx` |
| Executive narrative | Python + optional AI | `reports/executive_summary.md` |
| Portfolio README | Markdown | `README.md` |

### Automation flow

```
data_cleaning.py → load_to_database.py → generate_kpi_report.py → ai_executive_summary.py
```

---

## 7. Evaluation & Iteration

### V1 completion checklist

- [ ] All KPIs return real results from Olist data
- [ ] Dashboard screenshots in README
- [ ] No hardcoded / fabricated numbers in scripts
- [ ] Data dictionary matches actual schema
- [ ] Repeat purchase rate and CLV validated against notebook

### V2 roadmap

- Google Analytics funnel and traffic sources
- Marketing campaign ROI and channel attribution
- Cohort retention by acquisition month

---

## Tools by phase

| Phase | Primary tools |
|-------|---------------|
| Cleaning | Python, Pandas, Jupyter |
| Modeling | SQL, SQLite |
| Analysis | SQL, Jupyter |
| Visualization | Power BI, Excel |
| Automation | Python, GitHub |
| Narrative | Markdown, optional LLM API |

---

## Documentation standards

- Every KPI has a one-line business definition in `data_dictionary.md`
- SQL files numbered in execution order (`01` → `06`)
- Python functions include docstrings; no fake output
- README project status updated at each phase gate
