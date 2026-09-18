CREATE SCHEMA IF NOT EXISTS dashboard;

-- =========================
-- STORE DIMENSION
-- =========================
CREATE TABLE IF NOT EXISTS dashboard.dim_store (
    store_sk SERIAL PRIMARY KEY,
    store_id VARCHAR(20) NOT NULL UNIQUE,
    store_name VARCHAR(200),
    address TEXT,
    city VARCHAR(100)
);

-- =========================
-- CATEGORY DIMENSION
-- =========================
CREATE TABLE IF NOT EXISTS dashboard.dim_category (
    category_sk SERIAL PRIMARY KEY,
    category_id VARCHAR(20) NOT NULL UNIQUE,
    category_name VARCHAR(200) NOT NULL
);

-- =========================
-- PRODUCT DIMENSION
-- =========================
CREATE TABLE IF NOT EXISTS dashboard.dim_product (
    product_sk SERIAL PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL,
    product_name VARCHAR(200),
    category_sk INTEGER REFERENCES dashboard.dim_category(category_sk),
    valid_from DATE NOT NULL,
    valid_to DATE
);

-- =========================
-- DATE DIMENSION
-- =========================
CREATE TABLE IF NOT EXISTS dashboard.dim_date (
    date_sk INTEGER PRIMARY KEY,
    calendar_date DATE NOT NULL UNIQUE,
    day INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    month INTEGER,
    month_name VARCHAR(20),
    year INTEGER
);

-- =========================
-- SALES FACT
-- =========================
CREATE TABLE IF NOT EXISTS dashboard.fact_sales (
    sales_sk BIGSERIAL PRIMARY KEY,
    bill_no VARCHAR(100) NOT NULL,
    line_no INTEGER NOT NULL,
    date_sk INTEGER REFERENCES dashboard.dim_date(date_sk),
    store_sk INTEGER REFERENCES dashboard.dim_store(store_sk),
    product_sk INTEGER REFERENCES dashboard.dim_product(product_sk),
    line_type VARCHAR(20) NOT NULL,
    qty NUMERIC,
    unit_price NUMERIC(18,2),
    revenue_amount NUMERIC(18,2),

    UNIQUE (bill_no, line_no)
);