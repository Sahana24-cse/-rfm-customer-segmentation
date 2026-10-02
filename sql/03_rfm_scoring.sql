-- 03_rfm_scoring.sql
-- ---------------------------------------------------------
-- Scores each customer 1-5 on Recency, Frequency, and Monetary
-- using NTILE(5), i.e. quintiles based on the ACTUAL distribution
-- of this dataset (not fixed/hardcoded thresholds).
--
-- Recency:   fewer days = more recent = BETTER, so it is scored
--            in reverse (smallest recency_days -> score 5).
-- Frequency: more orders = BETTER, scored directly (smallest -> 1).
-- Monetary:  more spend  = BETTER, scored directly (smallest -> 1).
-- ---------------------------------------------------------

WITH customer_agg AS (
    SELECT
        customer_id,
        MAX(order_date)          AS last_order_date,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(amount)               AS monetary
    FROM transactions
    GROUP BY customer_id
),

rfm_raw AS (
    SELECT
        customer_id,
        last_order_date,
        CAST(julianday('2024-12-31') - julianday(last_order_date) AS INTEGER) AS recency_days,
        frequency,
        monetary
    FROM customer_agg
),

rfm_scored AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,
        -- Recency: order ASC (smallest days first) then flip with 6 - ntile
        (6 - NTILE(5) OVER (ORDER BY recency_days ASC))  AS r_score,
        -- Frequency: smallest count = weakest = score 1
        NTILE(5) OVER (ORDER BY frequency ASC)           AS f_score,
        -- Monetary: smallest spend = weakest = score 1
        NTILE(5) OVER (ORDER BY monetary ASC)            AS m_score
    FROM rfm_raw
)

SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score)          AS rfm_total_score,
    (CAST(r_score AS TEXT) || CAST(f_score AS TEXT) || CAST(m_score AS TEXT)) AS rfm_code
FROM rfm_scored
ORDER BY rfm_total_score DESC;
