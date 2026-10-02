-- 02_rfm_calculation.sql
-- ---------------------------------------------------------
-- Calculates raw Recency, Frequency, Monetary values per customer.
--
--   Recency  = days since the customer's last order (as of SNAPSHOT_DATE)
--   Frequency = total number of distinct orders placed
--   Monetary  = total amount spent across all orders
--
-- SNAPSHOT_DATE = the "as of today" date for the analysis.
-- In production this would usually be CURRENT_DATE; here we hardcode
-- it to match the sample dataset's generation window.
-- ---------------------------------------------------------

WITH customer_agg AS (
    SELECT
        customer_id,
        MAX(order_date)            AS last_order_date,
        COUNT(DISTINCT order_id)   AS frequency,
        SUM(amount)                AS monetary
    FROM transactions
    GROUP BY customer_id
)

SELECT
    customer_id,
    last_order_date,
    -- SQLite: julianday() ; PostgreSQL: '2024-12-31'::date - last_order_date
    -- MySQL:   DATEDIFF('2024-12-31', last_order_date)
    CAST(julianday('2024-12-31') - julianday(last_order_date) AS INTEGER) AS recency_days,
    frequency,
    monetary
FROM customer_agg
ORDER BY recency_days ASC;
