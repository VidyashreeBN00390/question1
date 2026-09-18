CREATE SCHEMA IF NOT EXISTS dashboard;

-- =====================================================
-- 1. STORE DIMENSION
-- =====================================================
CREATE TABLE IF NOT EXISTS dashboard.dim_store (
    store_sk SERIAL PRIMARY KEY,
    store_id TEXT NOT NULL UNIQUE,
    store_name TEXT NOT NULL,
    address_line TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    region TEXT NOT NULL,
    floor_area_sqft INTEGER,
    opened_on DATE
);

-- =====================================================
-- 2. CATEGORY DIMENSION
-- =====================================================
CREATE TABLE IF NOT EXISTS dashboard.dim_category (
    category_sk SERIAL PRIMARY KEY,
    category_id TEXT NOT NULL UNIQUE,
    category_name TEXT NOT NULL,
    department TEXT,
    gst_rate NUMERIC(4,3)
);

-- =====================================================
-- 3. PRODUCT DIMENSION
-- =====================================================
CREATE TABLE IF NOT EXISTS dashboard.dim_product (
    product_sk BIGINT PRIMARY KEY,
    product_code TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category_sk INTEGER REFERENCES dashboard.dim_category(category_sk),
    brand TEXT,
    pack_size TEXT,
    uom TEXT,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    is_current BOOLEAN NOT NULL
);

-- =====================================================
-- 4. DATE DIMENSION
-- =====================================================
CREATE TABLE IF NOT EXISTS dashboard.dim_date (
    date_sk INTEGER PRIMARY KEY,
    calendar_date DATE NOT NULL UNIQUE,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    year INTEGER NOT NULL
);

-- =====================================================
-- 5. SALES FACT
-- =====================================================
CREATE TABLE IF NOT EXISTS dashboard.fact_sales (
    sales_sk BIGSERIAL PRIMARY KEY,

    bill_no TEXT NOT NULL,
    line_no INTEGER NOT NULL,

    date_sk INTEGER REFERENCES dashboard.dim_date(date_sk),
    store_sk INTEGER REFERENCES dashboard.dim_store(store_sk),
    product_sk BIGINT REFERENCES dashboard.dim_product(product_sk),

    line_type TEXT NOT NULL,

    qty NUMERIC,
    unit_price NUMERIC(18,2),
    revenue_amount NUMERIC(18,2),

    UNIQUE (bill_no, line_no)
);