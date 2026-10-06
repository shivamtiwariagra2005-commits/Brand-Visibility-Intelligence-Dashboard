"""
Brand Visibility Intelligence Dashboard
Step 2: Merge API data + provided dirty dataset, then clean it.

Usage:
    python clean_merge.py

Inputs (must be in the same folder, or update the paths below):
    - api_raw_data.csv        (from extract_data.py)
    - brand_dirty_dataset.csv (provided dataset)

Output:
    - cleaned_data.csv
"""

import re
import pandas as pd
import numpy as np

API_FILE = "api_raw_data.csv"
DIRTY_FILE = "brand_dirty_dataset.csv"
OUTPUT_FILE = "cleaned_data.csv"


# ----------------------------------------------------------------------
# 1. LOAD
# ----------------------------------------------------------------------
def load_data():
    api_df = pd.read_csv(API_FILE)
    dirty_df = pd.read_csv(DIRTY_FILE)

    print("API data shape:", api_df.shape)
    print("API columns:", list(api_df.columns))
    print()
    print("Dirty dataset shape:", dirty_df.shape)
    print("Dirty dataset columns:", list(dirty_df.columns))

    return api_df, dirty_df


# ----------------------------------------------------------------------
# 2. ALIGN COLUMNS
# ----------------------------------------------------------------------
def align_columns(api_df: pd.DataFrame, dirty_df: pd.DataFrame):
    """
    Standardize column names across both datasets so concat() lines up correctly.
    """
    api_df = api_df.drop(columns=["price"], errors="ignore")
    api_df = api_df.rename(columns={"extracted_price": "price"})

    dirty_df = dirty_df.rename(columns=lambda c: c.strip().lower().replace(" ", "_"))

    target_cols = [
        "keyword", "position", "title", "price", "old_price", "rating",
        "reviews", "platform", "delivery", "link", "thumbnail"
    ]

    for col in target_cols:
        if col not in api_df.columns:
            api_df[col] = np.nan
        if col not in dirty_df.columns:
            dirty_df[col] = np.nan

    api_df = api_df[target_cols]
    dirty_df = dirty_df[target_cols]

    return api_df, dirty_df


# ----------------------------------------------------------------------
# 3. MERGE
# ----------------------------------------------------------------------
def merge_data(api_df: pd.DataFrame, dirty_df: pd.DataFrame) -> pd.DataFrame:
    combined = pd.concat([api_df, dirty_df], ignore_index=True)
    print("\nCombined shape before cleaning:", combined.shape)
    return combined


# ----------------------------------------------------------------------
# 4. CLEAN
# ----------------------------------------------------------------------
def clean_price(value):
    """Convert messy price strings like '$29.12', 'Not Available' to float or NaN."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value)
    value = re.sub(r"[^\d.]", "", value)
    if value in ("", "."):
        return np.nan
    try:
        return float(value)
    except ValueError:
        return np.nan


def extract_raw_price(value):
    """Extract original/MRP price from strings like '70% off₹4,999'."""
    if pd.isna(value):
        return np.nan

    value = str(value)

    # Remove discount part such as "70% off"
    value = re.sub(r"\d+(?:\.\d+)?%\s*off", "", value, flags=re.IGNORECASE)

    # Keep only digits and decimal point
    value = re.sub(r"[^\d.]", "", value)

    if value in ("", "."):
        return np.nan

    try:
        return float(value)
    except ValueError:
        return np.nan

def clean_numeric(value):
    """Convert messy numeric-ish strings like 'many', 'N/A' to NaN, else float."""
    if pd.isna(value):
        return np.nan
    try:
        return float(value)
    except (ValueError, TypeError):
        return np.nan


def clean_title(title):
    if pd.isna(title):
        return title
    title = str(title)
    title = re.sub(r"[^\w\s\-&.]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


KNOWN_BRANDS = [
    "Apple", "Macbook", "Samsung", "Boat", "BoAt", "Sony", "Dell", "HP", "Hp",
    "Puma", "Nike", "Philips", "LG", "Lg", "Redmi", "Realme", "Noise",
    "Zebronics", "Motorola", "Oppo", "Xiaomi", "Mi", "Poco", "OnePlus",
    "Adidas", "Titan", "Fastrack", "Fire-Boltt", "Tata", "Croma", "Iqoo",
    "Vivo", "Asus", "Acer", "Lenovo", "Ideapad", "Bata", "Skechers",
    "Woodland", "Campus", "Bersache", "Sparx", "Reebok", "Fila",
    "Anker", "Tangzu", "Hammer", "Impakto", "Goboult", "Boldfit",
    "Ptron", "Portronics", "Zinq", "Duke", "Crocs", "Under Armour",
]


def extract_brand(title):
    """
    Brand extraction: match against a known-brand list (case-insensitive
    substring match). Falls back to the first word of the title if no
    known brand is found, or 'Unknown' if the title is empty.
    """
    if pd.isna(title) or title == "":
        return "Unknown"
    title_str = str(title)
    title_lower = title_str.lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in title_lower:
            return brand.title() if brand.lower() != "boat" else "Boat"
    return title_str.split()[0].strip().title()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["price"] = df["price"].apply(clean_price)
    df["raw_price"] = df["old_price"].apply(extract_raw_price)
    df["rating"] = df["rating"].apply(clean_numeric)
    df["reviews"] = df["reviews"].apply(clean_numeric)
    df["position"] = df["position"].apply(clean_numeric)
    df["title"] = df["title"].apply(clean_title)

    df["platform"] = df["platform"].astype(str).str.strip().str.title()
    df["platform"] = df["platform"].replace({"Nan": np.nan})

    df["delivery"] = df["delivery"].fillna("Unknown")

    df = df[df["title"].notna() & (df["title"] != "")]

    before = len(df)
    df = df.drop_duplicates(subset=["title", "price"])
    print(f"Removed {before - len(df)} duplicate rows")

    df = df[(df["price"].isna()) | (df["price"] > 0)]

    if df["price"].notna().sum() > 0:
        cap = df["price"].quantile(0.99)
        df["price"] = df["price"].clip(upper=cap)

    df["brand"] = df["title"].apply(extract_brand)

    max_pos = df["position"].max()
    df["visibility_score"] = df["position"].apply(
        lambda p: round(1 - (p - 1) / max_pos, 3) if pd.notna(p) and max_pos and max_pos > 0 else np.nan
    )

    df["price_range"] = pd.cut(
        df["price"],
        bins=[0, 500, 1500, 5000, 20000, np.inf],
        labels=["Very Low", "Low", "Medium", "High", "Very High"]
    )
    df["price_range_sort"] = df["price_range"].map({
        "Very Low": 1,
        "Low": 2,
        "Medium": 3,
        "High": 4,
        "Very High": 5
    })
    # Calculate discount percentage only when a valid original/MRP price is available.
    # Missing original prices remain NaN instead of being treated as zero discount.
    # A discount is valid only when the original price is greater than the current price.
    valid_discount = (
            df["raw_price"].notna()
            & df["price"].notna()
            & (df["raw_price"] > df["price"])
            & (df["raw_price"] > 0)
    )

    df["discount_pct"] = np.where(
        valid_discount,
        ((df["raw_price"] - df["price"]) / df["raw_price"] * 100).round(2),
        np.nan
    )
    return df


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    api_df, dirty_df = load_data()
    api_df, dirty_df = align_columns(api_df, dirty_df)
    combined = merge_data(api_df, dirty_df)
    cleaned = clean_data(combined)

    cleaned.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved cleaned dataset: {OUTPUT_FILE}")
    print("Final shape:", cleaned.shape)
    print("\nMissing values per column:\n", cleaned.isna().sum())
    print("\nSample rows:\n", cleaned.head())


if __name__ == "__main__":
    main()