DROP TABLE IF EXISTS voucher_segmentation;

-- create result table by a query
CREATE TABLE IF NOT EXISTS voucher_segmentation AS (

    -- clean the data with the following criteria
    WITH valid_data AS (
        SELECT *,
            CASE
                WHEN country_code != 'Peru' THEN FALSE
                WHEN total_orders IS NULL THEN FALSE
                WHEN voucher_amount IS NULL THEN FALSE
                WHEN total_orders = 0 AND (last_order_ts IS NOT NULL OR first_order_ts IS NOT NULL) THEN FALSE
                WHEN total_orders = 1 AND (last_order_ts != first_order_ts) THEN FALSE
                WHEN last_order_ts < first_order_ts THEN FALSE
                ELSE TRUE
            END AS valid
        from voucher_history
    ),

    featured_data AS (
        SELECT
            voucher_amount,
            total_orders,
            ('2020-06-01'::DATE - last_order_ts::DATE) AS recency_days
        FROM valid_data WHERE valid
    ),

    quantized_data AS (
        SELECT
            voucher_amount,
            CASE
                WHEN total_orders BETWEEN 0 AND 4 THEN '0-4'
                WHEN total_orders BETWEEN 5 AND 13 THEN '5-13'
                WHEN total_orders BETWEEN 14 AND 37 THEN '14-37'
                WHEN total_orders > 37 THEN 'other'
            END AS quantized_frequency,
            CASE
                WHEN recency_days BETWEEN 0 AND 29 THEN 'other'
                WHEN recency_days BETWEEN 30 AND 60 THEN '30-60'
                WHEN recency_days BETWEEN 61 AND 90 THEN '61-90'
                WHEN recency_days BETWEEN 91 AND 120 THEN '91-120'
                WHEN recency_days BETWEEN 121 AND 180 THEN '121-180'
                WHEN recency_days > 180 THEN '180'
            END AS quantized_recency
        FROM featured_data
    ),

    frequency_counts AS (
        SELECT
            voucher_amount,
            quantized_frequency,
            COUNT(*) AS counts
        FROM quantized_data
        GROUP BY voucher_amount, quantized_frequency
    ),

    top_frequency_counts AS (
        SELECT
            voucher_amount,
            quantized_frequency,
            ROW_NUMBER() OVER (PARTITION BY quantized_frequency ORDER BY counts DESC) AS rank
        FROM frequency_counts
    ),

    frequency_segments AS (
        SELECT
            voucher_amount,
            quantized_frequency AS segment_name,
            'frequent_segment' AS segment_type
        FROM top_frequency_counts where rank=1
    ),

    recency_counts AS (
        SELECT
            voucher_amount,
            quantized_recency,
            COUNT(*) AS counts
        FROM quantized_data
        GROUP BY voucher_amount, quantized_recency
    ),

    top_recency_counts AS (
        SELECT
            voucher_amount,
            quantized_recency,
            ROW_NUMBER() OVER (PARTITION BY quantized_recency ORDER BY counts DESC) AS rank
        FROM recency_counts
    ),

    recency_segments AS (
        SELECT
            voucher_amount,
            quantized_recency AS segment_name,
            'recency_segment' AS segment_type
        FROM top_recency_counts where rank=1
    )


SELECT * FROM recency_segments
UNION ALL
SELECT * FROM frequency_segments
);