-- query to copy CSV file to a table
COPY voucher_history (
    timestamp,
    country_code,
    last_order_ts,
    first_order_ts,
    total_orders,
    voucher_amount
)
FROM STDIN DELIMITER ',' CSV HEADER;