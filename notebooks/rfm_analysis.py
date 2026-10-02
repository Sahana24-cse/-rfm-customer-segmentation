"""
rfm_analysis.py
------------------------
Pandas-based RFM analysis. Mirrors the SQL logic in sql/02, 03, 04
so you can validate the SQL output, and produces charts +
a segment_summary.csv for the dashboard.

Run:  python3 notebooks/rfm_analysis.py
(run from the project root so relative paths resolve)
"""

import pandas as pd
import matplotlib.pyplot as plt

SNAPSHOT_DATE = pd.Timestamp("2024-12-31")

# ---------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------
df = pd.read_csv("data/raw/retail_transactions.csv", parse_dates=["order_date"])
print(f"Loaded {len(df)} transactions for {df['customer_id'].nunique()} customers.")

# ---------------------------------------------------------
# 2. Calculate raw Recency, Frequency, Monetary per customer
# ---------------------------------------------------------
rfm = df.groupby("customer_id").agg(
    last_order_date=("order_date", "max"),
    frequency=("order_id", "nunique"),
    monetary=("amount", "sum")
).reset_index()

rfm["recency_days"] = (SNAPSHOT_DATE - rfm["last_order_date"]).dt.days

# ---------------------------------------------------------
# 3. Score each metric 1-5 using quintiles (qcut)
#    Recency is reversed: fewer days = higher score
# ---------------------------------------------------------
rfm["r_score"] = pd.qcut(rfm["recency_days"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

rfm["rfm_total_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
rfm["rfm_code"] = (
    rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)
)

# ---------------------------------------------------------
# 4. Map scores to business segments
# ---------------------------------------------------------
def assign_segment(row):
    r, f, m = row["r_score"], row["f_score"], row["m_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 2:
        return "New Customers"
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Lost / Hibernating"
    elif r >= 3 and f <= 2 and m <= 2:
        return "Potential Loyalist"
    else:
        return "Needs Attention"

rfm["segment"] = rfm.apply(assign_segment, axis=1)

# ---------------------------------------------------------
# 5. Segment summary (for dashboard / stakeholders)
# ---------------------------------------------------------
summary = rfm.groupby("segment").agg(
    num_customers=("customer_id", "count"),
    total_revenue=("monetary", "sum"),
    avg_recency_days=("recency_days", "mean"),
    avg_frequency=("frequency", "mean")
).sort_values("total_revenue", ascending=False)

summary["pct_of_customers"] = (summary["num_customers"] / summary["num_customers"].sum() * 100).round(1)
summary["pct_of_revenue"] = (summary["total_revenue"] / summary["total_revenue"].sum() * 100).round(1)

print("\n=== Segment Summary ===")
print(summary)

rfm.to_csv("reports/rfm_customer_scores.csv", index=False)
summary.to_csv("reports/segment_summary.csv")
print("\nSaved: reports/rfm_customer_scores.csv, reports/segment_summary.csv")

# ---------------------------------------------------------
# 6. Visualizations
# ---------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(13, 10))

# Segment size (customer count)
summary["num_customers"].plot(kind="bar", ax=axes[0, 0], color="#4C72B0")
axes[0, 0].set_title("Number of Customers per Segment")
axes[0, 0].set_ylabel("Customers")
axes[0, 0].tick_params(axis="x", rotation=45)

# Revenue contribution by segment
summary["total_revenue"].plot(kind="bar", ax=axes[0, 1], color="#55A868")
axes[0, 1].set_title("Total Revenue by Segment")
axes[0, 1].set_ylabel("Revenue")
axes[0, 1].tick_params(axis="x", rotation=45)

# Recency distribution
axes[1, 0].hist(rfm["recency_days"], bins=30, color="#C44E52")
axes[1, 0].set_title("Recency Distribution (days since last order)")
axes[1, 0].set_xlabel("Days")

# Segment share (pie)
axes[1, 1].pie(
    summary["num_customers"],
    labels=summary.index,
    autopct="%1.0f%%",
    textprops={"fontsize": 8}
)
axes[1, 1].set_title("Customer Share by Segment")

plt.tight_layout()
plt.savefig("reports/figures_rfm_overview.png", dpi=150)
print("Saved chart: reports/figures_rfm_overview.png")
