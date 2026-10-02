-- 04_segment_mapping.sql
-- ---------------------------------------------------------
-- Final view: takes the R/F/M scores from 03_rfm_scoring.sql
-- and maps them to human-readable business segments using
-- CASE WHEN logic. This is the query the dashboard (Power BI /
-- Excel / Streamlit) should connect to.
-- ---------------------------------------------------------

DROP VIEW IF EXISTS customer_rfm_segments;

CREATE VIEW customer_rfm_segments AS
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
        last_order_date,
        recency_days,
        frequency,
        monetary,
        (6 - NTILE(5) OVER (ORDER BY recency_days ASC)) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)          AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)           AS m_score
    FROM rfm_raw
)

SELECT
    customer_id,
    last_order_date,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score) AS rfm_total_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4
            THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3
            THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2
            THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3
            THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2
            THEN 'Lost / Hibernating'
        WHEN r_score >= 3 AND f_score <= 2 AND m_score <= 2
            THEN 'Potential Loyalist'
        ELSE 'Needs Attention'
    END AS segment
FROM rfm_scored;

-- Example usage:
-- SELECT segment, COUNT(*) AS num_customers, SUM(monetary) AS total_revenue
-- FROM customer_rfm_segments
-- GROUP BY segment
-- ORDER BY total_revenue DESC;

SELECT * FROM customer_rfm_segments ORDER BY rfm_total_score DESC;
