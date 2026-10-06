"""
Brand Visibility Intelligence Dashboard
Step 3: Load cleaned data into MySQL

Usage:
    1. pip install sqlalchemy pymysql pandas
    2. Set the MYSQL_PASSWORD environment variable before running the script.
    3. Run: python load_to_sql.py
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# ----------------------------------------------------------------------
# CONFIG - update these
# ----------------------------------------------------------------------
MYSQL_USER = "root"
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB = "brand_visibility_db"

CSV_FILE = "cleaned_data.csv"
TABLE_NAME = "products"


def main():
    if not MYSQL_PASSWORD:
        raise SystemExit(
            "MYSQL_PASSWORD is not set. "
            "Configure the MYSQL_PASSWORD environment variable before running."
        )

    # Build connection string
    connection_str = (
        f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    engine = create_engine(connection_str)

    # Load cleaned CSV
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns from {CSV_FILE}")

    # Write to MySQL (replaces table if it already exists)
    df.to_sql(TABLE_NAME, con=engine, if_exists="replace", index=False)
    print(f"Loaded data into MySQL table '{TABLE_NAME}' in database '{MYSQL_DB}'")

    # Quick sanity check - read back row count
    with engine.connect() as conn:
        result = conn.exec_driver_sql(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        count = result.scalar()
        print(f"Verified: {count} rows now in MySQL table '{TABLE_NAME}'")


if __name__ == "__main__":
    main()