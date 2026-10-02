-- 01_create_tables.sql
-- ---------------------------------------------------------
-- Creates the base transactions table.
-- Works on SQLite / PostgreSQL / MySQL (minor type tweaks noted).
-- Load data/raw/retail_transactions.csv into this table before
-- running the rest of the scripts.
-- ---------------------------------------------------------

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    customer_id   TEXT NOT NULL,      -- MySQL/Postgres: VARCHAR(20)
    order_id      TEXT NOT NULL,      -- MySQL/Postgres: VARCHAR(20)
    order_date    DATE NOT NULL,
    amount        DECIMAL(10, 2) NOT NULL
);

-- SQLite example load (run from sqlite3 CLI, not as SQL):
-- .mode csv
-- .import data/raw/retail_transactions.csv transactions --skip 1

-- PostgreSQL example load:
-- \copy transactions FROM 'data/raw/retail_transactions.csv' DELIMITER ',' CSV HEADER;

CREATE INDEX idx_transactions_customer ON transactions (customer_id);
CREATE INDEX idx_transactions_date ON transactions (order_date);
