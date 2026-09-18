import duckdb
import pandas as pd
import psycopg
from pathlib import Path

DATA_DIR = Path(r"C:\Users\ub02-glab-067\Desktop\data")
PARQUET_PATH = DATA_DIR / "output" / "sales_parquet"

PG_CONN = (
    "host=localhost "
    "port=5432 "
    "dbname=annapoorna "
    "user=annapoorna "
    "password=postgres123"
)

pg = psycopg.connect(PG_CONN)

products = pd.read_sql(
    """
    SELECT
        product_sk,
        product_code,
        valid_from,
        valid_to
    FROM dashboard.dim_product
    """,
    pg
)

con = duckdb.connect()

con.register("dim_product", products)

parquet_path = str(PARQUET_PATH / "**" / "*.parquet")

query = f"""
SELECT
    COUNT(*) AS total_sales_rows,
    COUNT(DISTINCT s.bill_no || '|' || CAST(s.line_no AS VARCHAR))
        AS distinct_sales_lines,
    COUNT(*) - COUNT(DISTINCT s.bill_no || '|' || CAST(s.line_no AS VARCHAR))
        AS extra_matches
FROM read_parquet(
    '{parquet_path}',
    hive_partitioning=true
) s
JOIN dim_product p
    ON s.product_code = p.product_code
    AND CAST(s.business_date AS DATE)
        BETWEEN p.valid_from AND p.valid_to;
"""

print("=" * 60)
print("PRODUCT TEMPORAL JOIN CHECK")
print("=" * 60)

result = con.execute(query).fetchdf()

print(result.to_string(index=False))

print("=" * 60)

pg.close()
con.close()