from pathlib import Path
import pandas as pd
import re
import hashlib

# --------------------------------------------------
# PATHS
# --------------------------------------------------

SALES_DIR = Path(
    r"C:\Users\ub02-glab-067\Desktop\data\data\sales"
)

OUTPUT_DIR = Path(
    r"C:\Users\ub02-glab-067\Desktop\data\output\sales_parquet"
)

if OUTPUT_DIR.exists():
    import shutil
    shutil.rmtree(OUTPUT_DIR)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# EXTRACT STORE + BUSINESS DATE
# --------------------------------------------------

def get_store_and_date(filename):

    match = re.search(
        r"SALES_(S\d{2})_(\d{8})",
        filename
    )

    if not match:
        raise ValueError(
            f"Cannot identify store/date: {filename}"
        )

    store_id = match.group(1)

    date_string = match.group(2)

    business_date = pd.to_datetime(
        date_string,
        format="%Y%m%d"
    ).date()

    return store_id, business_date


# --------------------------------------------------
# READ + NORMALIZE ONE FILE
# --------------------------------------------------

def read_sales_file(file_path):

    filename = file_path.name

    store_id, business_date = get_store_and_date(
        filename
    )

    # -------------------------
    # CSV / PARQUET
    # -------------------------

    if file_path.suffix.lower() == ".parquet":

        df = pd.read_parquet(file_path)

    elif file_path.suffix.lower() == ".csv":

        if store_id in ["S06", "S07", "S08", "S09"]:

            df = pd.read_csv(
                file_path,
                sep=";"
            )

        elif store_id in ["S10", "S11", "S12"]:

            df = pd.read_csv(
                file_path,
                encoding="utf-8-sig"
            )

        else:

            df = pd.read_csv(
                file_path
            )

    else:

        raise ValueError(
            f"Unsupported file: {file_path}"
        )

    # -------------------------
    # NORMALIZE COLUMN NAMES
    # -------------------------

    column_mapping = {
        "item_code": "product_code",
        "quantity": "qty",
        "rate": "unit_price",
        "type": "line_type",
        "txn_time": "ts"
    }

    df = df.rename(
        columns=column_mapping
    )

    # -------------------------
    # NORMALIZE TIMESTAMP
    # -------------------------

    if store_id in ["S10", "S11", "S12"]:

        df["ts"] = pd.to_datetime(
            df["ts"],
            unit="s",
            utc=True
        )

    elif store_id in ["S06", "S07", "S08", "S09"]:

        df["ts"] = pd.to_datetime(
            df["ts"],
            format="%d-%m-%Y %H:%M:%S"
        )

    else:

        df["ts"] = pd.to_datetime(
            df["ts"]
        )

    # -------------------------
    # ADD METADATA
    # -------------------------

    df["store_id"] = store_id

    df["business_date"] = pd.to_datetime(
        business_date
    )

    df["source_file"] = filename

    # -------------------------
    # STANDARD COLUMNS
    # -------------------------

    columns = [
        "bill_no",
        "line_no",
        "product_code",
        "qty",
        "unit_price",
        "line_type",
        "ts",
        "store_id",
        "business_date",
        "source_file"
    ]

    df = df[columns]

    return df


# --------------------------------------------------
# FIND ALL SALES FILES
# --------------------------------------------------

files = [
    f for f in SALES_DIR.rglob("*")
    if f.is_file()
    and f.suffix.lower() in [".csv", ".parquet"]
]

print("=" * 60)
print("ANNAPOORNA SALES INGESTION")
print("=" * 60)

print("Sales files found:", len(files))


# --------------------------------------------------
# READ ALL FILES
# --------------------------------------------------

all_data = []

failed_files = []

for i, file_path in enumerate(files, start=1):

    try:

        df = read_sales_file(file_path)

        all_data.append(df)

    except Exception as e:

        failed_files.append(
            (str(file_path), str(e))
        )

    if i % 250 == 0:

        print(
            f"Processed {i}/{len(files)} files..."
        )


print("\nFinished reading files.")

print(
    "Files successfully read:",
    len(all_data)
)

print(
    "Files failed:",
    len(failed_files)
)


# --------------------------------------------------
# STOP IF ANY FILE FAILED
# --------------------------------------------------

if failed_files:

    print("\nFAILED FILES:")

    for file_name, error in failed_files:

        print(file_name)
        print(error)

    raise RuntimeError(
        "Some files could not be processed."
    )


# --------------------------------------------------
# COMBINE
# --------------------------------------------------

sales = pd.concat(
    all_data,
    ignore_index=True
)

print("\nRaw row count:")
print(len(sales))


# --------------------------------------------------
# CHECK DUPLICATE LINE KEYS
# --------------------------------------------------

duplicate_mask = sales.duplicated(
    subset=["bill_no", "line_no"],
    keep=False
)

duplicate_rows = sales[duplicate_mask]

print(
    "\nRows involved in duplicate keys:",
    len(duplicate_rows)
)


# --------------------------------------------------
# CHECK WHETHER DUPLICATES CONFLICT
# --------------------------------------------------

compare_columns = [
    "product_code",
    "qty",
    "unit_price",
    "line_type",
    "ts",
    "store_id",
    "business_date"
]

conflict_count = 0

if len(duplicate_rows) > 0:

    grouped = duplicate_rows.groupby(
        ["bill_no", "line_no"]
    )

    for key, group in grouped:

        if group[compare_columns].drop_duplicates().shape[0] > 1:

            conflict_count += 1

print(
    "Duplicate keys with conflicting data:",
    conflict_count
)


# --------------------------------------------------
# DEDUPLICATE BY LINE IDENTITY
# --------------------------------------------------

sales = sales.drop_duplicates(
    subset=["bill_no", "line_no"],
    keep="first"
).reset_index(drop=True)

print(
    "\nUnique row count after deduplication:"
)

print(len(sales))


# --------------------------------------------------
# ADD PARTITION COLUMNS
# --------------------------------------------------

sales["business_year"] = (
    sales["business_date"].dt.year
)

sales["business_month"] = (
    sales["business_date"].dt.month
)


# --------------------------------------------------
# WRITE PARTITIONED PARQUET
# --------------------------------------------------

print("\nWriting partitioned Parquet...")

sales.to_parquet(
    OUTPUT_DIR,
    engine="pyarrow",
    partition_cols=[
        "store_id",
        "business_year",
        "business_month",
        "business_date"
    ],
    index=False
)


# --------------------------------------------------
# CHECKSUM
# --------------------------------------------------

check_data = sales.sort_values(
    ["bill_no", "line_no"]
).copy()

check_data["checksum_text"] = (
    check_data["bill_no"].astype(str)
    + "|"
    + check_data["line_no"].astype(str)
    + "|"
    + check_data["product_code"].astype(str)
    + "|"
    + check_data["qty"].astype(str)
    + "|"
    + check_data["unit_price"].astype(str)
    + "|"
    + check_data["line_type"].astype(str)
    + "|"
    + check_data["ts"].astype(str)
    + "|"
    + check_data["store_id"].astype(str)
    + "|"
    + check_data["business_date"].astype(str)
)

sha = hashlib.sha256()

for value in check_data["checksum_text"]:

    sha.update(
        value.encode("utf-8")
    )

checksum = sha.hexdigest()


# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

print("\n" + "=" * 60)
print("FINAL INGESTION SUMMARY")
print("=" * 60)

print(
    "Total source files:",
    len(files)
)

print(
    "Raw rows:",
    len(duplicate_rows) + len(sales)
    if False else "see raw row count above"
)

print(
    "Unique rows:",
    len(sales)
)

print(
    "Duplicate rows removed:",
    len(duplicate_rows) - (
        len(duplicate_rows.groupby(
            ["bill_no", "line_no"]
        ))
        if len(duplicate_rows) > 0
        else 0
    )
)

print(
    "Conflicting duplicate keys:",
    conflict_count
)

print(
    "SHA-256:",
    checksum
)

print(
    "\nParquet output:",
    OUTPUT_DIR
)

print("\nDONE.")