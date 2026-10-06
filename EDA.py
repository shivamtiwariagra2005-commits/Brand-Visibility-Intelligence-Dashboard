"""
Brand Visibility Intelligence Dashboard
Step 4: EDA - Answers all 30 EDA questions from the project spec.

Usage:
    pip install pandas matplotlib seaborn
    python eda.py

Output:
    - Printed answers to all 30 questions in the console
    - Charts saved into a 'charts' folder
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CSV_FILE = "cleaned_data.csv"
CHARTS_DIR = "charts"

sns.set_theme(style="whitegrid")
os.makedirs(CHARTS_DIR, exist_ok=True)


def save_chart(fig, name):
    path = os.path.join(CHARTS_DIR, f"{name}.png")
    fig.savefig(path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    print(f"  [chart saved: {path}]")


def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    df = pd.read_csv(CSV_FILE)

    # ============================================================
    # GENERAL MARKET ANALYSIS
    # ============================================================
    section("GENERAL MARKET ANALYSIS")

    # Q1: Total products per keyword
    print("\nQ1. Total products per keyword:")
    q1 = df["keyword"].value_counts()
    print(q1)
    fig, ax = plt.subplots(figsize=(10, 5))
    q1.plot(kind="bar", ax=ax, color="steelblue")
    ax.set_title("Total Products per Keyword")
    ax.set_ylabel("Count")
    save_chart(fig, "01_products_per_keyword")

    # Q2: Overall average price
    print("\nQ2. Overall average price:", round(df["price"].mean(), 2))

    # Q3: Distribution of price
    print("\nQ3. Price distribution (see chart)")
    fig, ax = plt.subplots(figsize=(8, 5))
    df["price"].dropna().plot(kind="hist", bins=30, ax=ax, color="orange")
    ax.set_title("Price Distribution")
    ax.set_xlabel("Price")
    save_chart(fig, "03_price_distribution")

    # Q4: Average rating across all products
    print("\nQ4. Average rating across all products:", round(df["rating"].mean(), 2))

    # Q5: Reviews distribution (low vs high engagement)
    print("\nQ5. Reviews distribution stats:")
    print(df["reviews"].describe())
    fig, ax = plt.subplots(figsize=(8, 5))
    df["reviews"].dropna().plot(kind="hist", bins=30, ax=ax, color="green")
    ax.set_title("Reviews Distribution")
    save_chart(fig, "05_reviews_distribution")

    # ============================================================
    # BRAND ANALYSIS
    # ============================================================
    section("BRAND ANALYSIS")

    # Q6: Which brand appears most frequently?
    print("\nQ6. Most frequent brand:")
    q6 = df["brand"].value_counts().head(10)
    print(q6)
    fig, ax = plt.subplots(figsize=(10, 5))
    q6.plot(kind="bar", ax=ax, color="purple")
    ax.set_title("Top 10 Brands by Product Count")
    save_chart(fig, "06_top_brands_count")

    # Q7: Which brand has the highest average visibility_score?
    print("\nQ7. Brands with highest average visibility_score:")
    q7 = df.groupby("brand")["visibility_score"].mean().dropna().sort_values(ascending=False).head(10)
    print(q7)

    # Q8: Average position per brand
    print("\nQ8. Average position per brand (top 10 by count):")
    top_brands = df["brand"].value_counts().head(10).index
    q8 = df[df["brand"].isin(top_brands)].groupby("brand")["position"].mean().dropna()
    print(q8)

    # Q9: Brands most in top 10 positions
    print("\nQ9. Brands appearing most in top 10 positions:")
    q9 = df[df["position"] <= 10]["brand"].value_counts().head(10)
    print(q9)

    # Q10: Brands with highest average rating
    print("\nQ10. Brands with highest average rating (min 5 products):")
    brand_counts = df["brand"].value_counts()
    valid_brands = brand_counts[brand_counts >= 5].index
    q10 = df[df["brand"].isin(valid_brands)].groupby("brand")["rating"].mean().sort_values(ascending=False).head(10)
    print(q10)

    # ============================================================
    # PRICING ANALYSIS
    # ============================================================
    section("PRICING ANALYSIS")

    # Q11: Price distribution across brands
    print("\nQ11. Avg price by top 10 brands:")
    q11 = df[df["brand"].isin(top_brands)].groupby("brand")["price"].mean().sort_values(ascending=False)
    print(q11)
    fig, ax = plt.subplots(figsize=(10, 5))
    q11.plot(kind="bar", ax=ax, color="teal")
    ax.set_title("Average Price by Top 10 Brands")
    save_chart(fig, "11_avg_price_by_brand")

    # Q12: Distribution across price_range categories
    print("\nQ12. Products per price range:")
    q12 = df["price_range"].value_counts()
    print(q12)
    fig, ax = plt.subplots(figsize=(8, 5))
    q12.plot(kind="bar", ax=ax, color="coral")
    ax.set_title("Products per Price Range")
    save_chart(fig, "12_price_range_distribution")

    # Q13: Do higher-priced products have better rankings?
    print("\nQ13. Correlation between price and position:")
    corr13 = df[["price", "position"]].corr().iloc[0, 1]
    print(f"  Correlation: {round(corr13, 3)}")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["price"], df["position"], alpha=0.4)
    ax.set_xlabel("Price")
    ax.set_ylabel("Position")
    ax.set_title("Price vs Position")
    save_chart(fig, "13_price_vs_position")

    # Q14: Average price per platform
    print("\nQ14. Average price per platform:")
    q14 = df.groupby("platform")["price"].mean().sort_values(ascending=False)
    print(q14)

    # Q15: Highest price products within each keyword
    print("\nQ15. Highest price products within each keyword:")
    q15_idx = df.dropna(subset=["price"]).groupby("keyword")["price"].idxmax()
    q15 = df.loc[q15_idx][["keyword", "title", "price"]]
    print(q15)

    # Q16: % of products with non-zero discount
    print("\nQ16. % products with non-zero discount:")
    if df["discount_pct"].notna().any():
        pct16 = (df["discount_pct"] > 0).mean() * 100
        print(f"  {round(pct16, 2)}%")
    else:
        print("  Discount data not available (no pre-discount/raw price in either source)")

    # Q17: Do discounted products have better rankings?
    print("\nQ17. Avg position: discounted vs non-discounted:")
    if df["discount_pct"].notna().any():
        q17 = df.groupby(df["discount_pct"] > 0)["position"].mean()
        print(q17)
    else:
        print("  Not available - discount data missing")

    # Q18: Brand with highest average discount
    print("\nQ18. Top 10 brands by average discount:")
    if df["discount_pct"].notna().any():
        q18 = df.groupby("brand")["discount_pct"].mean().dropna().sort_values(ascending=False).head(10)
        print(q18)
    else:
        print("  Not available - discount data missing")

    # Q19: Platform with highest average discount
    print("\nQ19. Average discount by platform:")
    if df["discount_pct"].notna().any():
        q19 = df.groupby("platform")["discount_pct"].mean().dropna().sort_values(ascending=False)
        print(q19)
    else:
        print("  Not available - discount data missing")

    # Q20: Relationship between discount and rating
    print("\nQ20. Correlation between discount_pct and rating:")
    if df["discount_pct"].notna().any():
        corr20 = df[["discount_pct", "rating"]].corr().iloc[0, 1]
        print(f"  Correlation: {round(corr20, 3)}")
    else:
        print("  Not available - discount data missing")

    # ============================================================
    # PLATFORM ANALYSIS
    # ============================================================
    section("PLATFORM ANALYSIS")

    # Q21: Platform with highest number of products
    print("\nQ21. Products per platform:")
    q21 = df["platform"].value_counts()
    print(q21)
    fig, ax = plt.subplots(figsize=(10, 5))
    q21.plot(kind="bar", ax=ax, color="navy")
    ax.set_title("Products per Platform")
    save_chart(fig, "21_products_per_platform")

    # Q22: Platform with highest average rating
    print("\nQ22. Average rating per platform:")
    q22 = df.groupby("platform")["rating"].mean().sort_values(ascending=False)
    print(q22)

    # Q23: Platform with lowest average price
    print("\nQ23. Average price per platform (lowest first):")
    q23 = df.groupby("platform")["price"].mean().sort_values()
    print(q23)

    # Q24: Average position per platform
    print("\nQ24. Average position per platform:")
    q24 = df.groupby("platform")["position"].mean().dropna().sort_values()
    print(q24)

    # Q25: Brands most frequently listed on each platform
    print("\nQ25. Top brand per platform:")
    q25 = df.groupby("platform")["brand"].agg(lambda x: x.value_counts().index[0] if len(x) > 0 else None)
    print(q25)

    # ============================================================
    # VISIBILITY & RANKING ANALYSIS
    # ============================================================
    section("VISIBILITY & RANKING ANALYSIS")

    # Q26: Distribution of position
    print("\nQ26. Position distribution stats:")
    print(df["position"].describe())
    fig, ax = plt.subplots(figsize=(8, 5))
    df["position"].dropna().plot(kind="hist", bins=20, ax=ax, color="crimson")
    ax.set_title("Position Distribution")
    save_chart(fig, "26_position_distribution")

    # Q27: Products with highest visibility_score
    print("\nQ27. Top 10 products by visibility_score:")
    q27 = df.dropna(subset=["visibility_score"]).sort_values("visibility_score", ascending=False).head(10)[["title", "brand", "visibility_score"]]
    print(q27)

    # Q28: Relationship between rating and position
    print("\nQ28. Correlation between rating and position:")
    corr28 = df[["rating", "position"]].corr().iloc[0, 1]
    print(f"  Correlation: {round(corr28, 3)}")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["rating"], df["position"], alpha=0.4, color="darkgreen")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Position")
    ax.set_title("Rating vs Position")
    save_chart(fig, "28_rating_vs_position")

    # Q29: Do products with higher reviews rank better?
    print("\nQ29. Correlation between reviews and position:")
    corr29 = df[["reviews", "position"]].corr().iloc[0, 1]
    print(f"  Correlation: {round(corr29, 3)}")

    # Q30: Combination of factors influencing top-ranking products
    print("\nQ30. Avg price/rating/reviews for top 10 positions vs rest:")
    df["is_top10"] = df["position"] <= 10
    q30 = df.groupby("is_top10")[["price", "rating", "reviews"]].mean()
    print(q30)

    print("\n\nAll 30 EDA questions answered. Charts saved in the 'charts' folder.")


if __name__ == "__main__":
    main()