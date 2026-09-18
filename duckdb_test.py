import duckdb

con = duckdb.connect()

query = """
SELECT
    COUNT(*) AS rows,
    ROUND(SUM(qty * unit_price), 2) AS gross_value
FROM read_parquet(
    'output/sales_parquet/**/*.parquet',
    hive_partitioning=true
)
WHERE store_id = 'S03'
  AND business_year = 2024
  AND business_month = 10;
"""

result = con.execute(query).fetchdf()

print("=" * 50)
print("DUCKDB ANALYTICAL QUERY")
print("=" * 50)
print(result)
print("=" * 50)