"""
Brand Visibility Intelligence Dashboard
Main Pipeline Runner

Runs the processing stages using the existing API dataset:
1. Clean and merge datasets
2. Load cleaned data into MySQL
3. Run Exploratory Data Analysis (EDA)

API extraction is kept separate to avoid unnecessary API requests.
"""

from Clean_Merge import main as clean_merge
from Load_to_SQL import main as load_to_sql
from EDA import main as run_eda


def main():
    print("=" * 70)
    print("BRAND VISIBILITY INTELLIGENCE DASHBOARD")
    print("=" * 70)

    print("\n[1/3] Cleaning and merging datasets...")
    clean_merge()

    print("\n[2/3] Loading cleaned data into MySQL...")
    load_to_sql()

    print("\n[3/3] Running exploratory data analysis...")
    run_eda()

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()