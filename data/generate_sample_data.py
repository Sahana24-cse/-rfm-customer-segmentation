"""
generate_sample_data.py
------------------------
Creates a synthetic retail transactions dataset so the RFM project
can be run end-to-end without needing a real company dataset.

Output: data/raw/retail_transactions.csv
Columns: customer_id, order_id, order_date, amount
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

NUM_CUSTOMERS = 500
SNAPSHOT_DATE = datetime(2024, 12, 31)   # "today" for recency calculation
START_DATE = SNAPSHOT_DATE - timedelta(days=365 * 2)  # 2 years of history

rows = []
order_id = 1000

for customer_id in range(1, NUM_CUSTOMERS + 1):
    # Give each customer a "behavior profile" so segments emerge naturally
    profile = np.random.choice(
        ["champion", "loyal", "at_risk", "new", "lost"],
        p=[0.10, 0.20, 0.20, 0.20, 0.30]
    )

    if profile == "champion":
        num_orders = np.random.randint(15, 30)
        recency_days = np.random.randint(0, 20)
        avg_amount = np.random.uniform(80, 200)
    elif profile == "loyal":
        num_orders = np.random.randint(8, 15)
        recency_days = np.random.randint(0, 45)
        avg_amount = np.random.uniform(50, 120)
    elif profile == "at_risk":
        num_orders = np.random.randint(6, 14)
        recency_days = np.random.randint(120, 250)
        avg_amount = np.random.uniform(60, 150)
    elif profile == "new":
        num_orders = np.random.randint(1, 3)
        recency_days = np.random.randint(0, 30)
        avg_amount = np.random.uniform(20, 90)
    else:  # lost
        num_orders = np.random.randint(1, 5)
        recency_days = np.random.randint(250, 400)
        avg_amount = np.random.uniform(10, 60)

    last_order_date = SNAPSHOT_DATE - timedelta(days=int(recency_days))

    # Spread the customer's past orders backwards from their last order date
    for i in range(num_orders):
        days_before_last = np.random.randint(0, 300)
        order_date = last_order_date - timedelta(days=int(days_before_last))
        if order_date < START_DATE:
            order_date = START_DATE + timedelta(days=np.random.randint(0, 30))

        amount = round(max(5, np.random.normal(avg_amount, avg_amount * 0.25)), 2)

        rows.append({
            "customer_id": f"CUST{customer_id:04d}",
            "order_id": f"ORD{order_id}",
            "order_date": order_date.strftime("%Y-%m-%d"),
            "amount": amount
        })
        order_id += 1

df = pd.DataFrame(rows)
df = df.sort_values(["customer_id", "order_date"]).reset_index(drop=True)

output_path = "data/raw/retail_transactions.csv"
df.to_csv(output_path, index=False)

print(f"Generated {len(df)} transactions for {NUM_CUSTOMERS} customers.")
print(f"Saved to: {output_path}")
print(df.head())
