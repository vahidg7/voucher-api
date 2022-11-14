-- initialize and create the voucher history table

DROP TABLE IF EXISTS voucher_history;

CREATE TABLE IF NOT EXISTS voucher_history (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    country_code VARCHAR(100),
    last_order_ts TIMESTAMP,
    first_order_ts TIMESTAMP,
    total_orders FLOAT,
    voucher_amount FLOAT
    );