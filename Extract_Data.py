"""
Brand Visibility Intelligence Dashboard
Step 1: API-based Data Extraction (Google Shopping via SerpApi)

Usage:
    1. pip install google-search-results pandas
    2. Set the SERPAPI_KEY environment variable before running the script.
    3. Edit KEYWORDS list to the product categories you want to track
    4. Run: python extract_data.py
    Output: api_raw_data.csv
"""

import os
import time
import pandas as pd
from serpapi import GoogleSearch

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
API_KEY = os.getenv("SERPAPI_KEY")

KEYWORDS = [
    "laptop",
    "smartphone",
    "shoes",
    "headphones",
    "smartwatch",
    # add more keywords relevant to your analysis
]

RESULTS_PER_KEYWORD = 40  # SerpApi paginates ~20-40 per page depending on engine
OUTPUT_FILE = "api_raw_data.csv"


def fetch_products_for_keyword(keyword: str) -> list[dict]:
    """Query Google Shopping via SerpApi for one keyword and return a list of product dicts."""
    params = {
        "engine": "google_shopping",
        "q": keyword,
        "api_key": API_KEY,
        "gl": "in",       # country - change to "us" etc. if needed
        "hl": "en",
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    shopping_results = results.get("shopping_results", [])

    records = []
    for item in shopping_results:
        records.append({
            "keyword": keyword,
            "position": item.get("position"),
            "title": item.get("title"),
            "price": item.get("price"),
            "extracted_price": item.get("extracted_price"),
            "old_price": item.get("old_price"),
            "rating": item.get("rating"),
            "reviews": item.get("reviews"),
            "platform": item.get("source"),
            "delivery": item.get("delivery"),
            "link": item.get("link") or item.get("product_link"),
            "thumbnail": item.get("thumbnail"),
        })
    return records


def main():
    if not API_KEY:
        raise SystemExit(
            "SERPAPI_KEY is not set. "
            "Configure the SERPAPI_KEY environment variable before running."
        )

    all_records = []
    for kw in KEYWORDS:
        print(f"Fetching results for keyword: '{kw}' ...")
        try:
            records = fetch_products_for_keyword(kw)
            print(f"  -> got {len(records)} products")
            all_records.extend(records)
        except Exception as e:
            print(f"  !! failed for '{kw}': {e}")
        time.sleep(1)  # be polite to the API

    df = pd.DataFrame(all_records)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved {len(df)} total rows to {OUTPUT_FILE}")
    print(df.head())


if __name__ == "__main__":
    main()