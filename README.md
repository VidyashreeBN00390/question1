The platform consists of:

Object store: MinIO
Relational database: PostgreSQL
Analytical query engine: DuckDB
Storage format: Parquet

sales/
└── store_id=S03/
    └── business_year=2024/
        └── business_month=10/
            ├── business_date=2024-10-01/
            │   └── part-0.parquet
            ├── business_date=2024-10-02/
            │   └── part-0.parquet
            └── ...
The partition hierarchy is:
store_id → business_year → business_month → business_date
For S03, October 2024:

Layout	Files potentially opened	Bytes potentially opened
Partitioned	31	402,414 bytes
One folder	4,389	44,785,182 bytes
This represents approximately:

99.29% reduction in files
99.10% reduction in bytes
