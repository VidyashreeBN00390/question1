import boto3
from pathlib import Path

# MinIO connection
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="Admin12345",
    region_name="us-east-1"
)

bucket = "annapurna"

# Parquet folder
root = Path(r"C:\Users\ub02-glab-067\Desktop\data\output\sales_parquet")

count = 0

for file in root.rglob("*.parquet"):
    relative_path = file.relative_to(root).as_posix()
    object_key = "sales/" + relative_path

    s3.upload_file(str(file), bucket, object_key)

    count += 1
    print(f"Uploaded: {object_key}")

print("\n================================")
print(f"Total Parquet files uploaded: {count}")
print("Upload completed successfully!")
print("================================")