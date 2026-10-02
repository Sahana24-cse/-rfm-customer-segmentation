# Customer Segmentation using RFM Analysis

Segments retail customers into groups like **Champions**, **Loyal Customers**,
**At Risk**, **New Customers**, and **Lost / Hibernating** using Recency,
Frequency, and Monetary (RFM) scoring — the same technique retail and
marketing teams use to decide who gets a loyalty reward vs. a win-back offer.

## Folder Structure

```
rfm-customer-segmentation/
├── data/
│   ├── generate_sample_data.py   # creates synthetic transactions if you don't have a real dataset
│   └── raw/
│       └── retail_transactions.csv
├── sql/
│   ├── 01_create_tables.sql      # base transactions table
│   ├── 02_rfm_calculation.sql    # raw Recency / Frequency / Monetary per customer
│   ├── 03_rfm_scoring.sql        # NTILE(5) quintile scoring
│   └── 04_segment_mapping.sql    # CASE WHEN -> named business segments (view)
├── notebooks/
│   └── rfm_analysis.py           # pandas version of the same logic + charts
├── dashboard/
│   └── app.py                    # Streamlit dashboard
├── reports/                      # generated CSVs + charts land here
├── requirements.txt
└── README.md
```

## How to Run

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate sample data** (skip this if you're using your own transactions CSV
   with columns `customer_id, order_id, order_date, amount`)
   ```bash
   python3 data/generate_sample_data.py
   ```

3. **Run the RFM analysis** (produces `reports/rfm_customer_scores.csv`,
   `reports/segment_summary.csv`, and a chart)
   ```bash
   python3 notebooks/rfm_analysis.py
   ```

4. **Launch the dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

5. **(Optional) Run the SQL version** — load `data/raw/retail_transactions.csv`
   into SQLite/PostgreSQL/MySQL using `sql/01_create_tables.sql`, then run
   `02`, `03`, and `04` in order. `04_segment_mapping.sql` creates a
   `customer_rfm_segments` view that a BI tool (Power BI, Tableau) can connect
   to directly.

## The RFM Logic

| Metric | Meaning | Scoring |
|---|---|---|
| Recency | Days since last order | Lower days = score 5 (most recent) |
| Frequency | Number of distinct orders | More orders = score 5 |
| Monetary | Total amount spent | More spend = score 5 |

Scores are combined (e.g., R=5, F=4, M=5) and mapped to a segment:

| Segment | Typical Pattern | Business Action |
|---|---|---|
| Champions | High R, F, M | Reward, upsell, ask for referrals |
| Loyal Customers | Good R, F, M | Nurture, loyalty programs |
| At Risk | Low R, high F/M | Win-back campaign, personalized offer |
| New Customers | High R, low F | Onboarding series, welcome discount |
| Lost / Hibernating | Low R, F, M | Low-cost reactivation or deprioritize |

## Tech Stack

- **SQL** (SQLite/PostgreSQL/MySQL compatible) — scoring logic, window functions (`NTILE`)
- **Python (pandas)** — validation of SQL logic, chart generation
- **Streamlit + Plotly** — interactive dashboard (swap for Power BI/Tableau/Excel if preferred)

## Notes on the Sample Dataset

`data/generate_sample_data.py` creates 500 synthetic customers with built-in
behavior profiles (champion, loyal, at_risk, new, lost) so the resulting
segments look realistic. Replace this with real transaction data by matching
the same CSV schema: `customer_id, order_id, order_date, amount`.
