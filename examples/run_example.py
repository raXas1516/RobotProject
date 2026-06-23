"""Runnable demo of the Multi-Channel Catalog Scaling pipeline.

Run from the repo root:  python examples/run_example.py

Demonstrates the pipeline across multiple product categories, with keyword
matching scoped to each product's category.
"""

import json
import os
import sys

# Allow running directly without installing the package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from catalog import CatalogPipeline, Product  # noqa: E402

PRODUCTS = [
    Product(
        title="Stainless Steel Rose Gold Pendant",
        raw_specs="Material: 316L Stainless Steel, Coating: 18k Rose Gold PVD, "
        "Chain Length: 18 inches, Skin: Hypoallergenic, Waterproof: Yes",
        sku="PND-RG-001",
        category="jewelry",
    ),
    Product(
        title="Brightening Vitamin C Face Serum",
        raw_specs="Active: Vitamin C 15%, Hydration: Hyaluronic Acid, "
        "Formula: Vegan, Testing: Dermatologist tested, Fragrance: Fragrance-free",
        sku="SRM-VC-002",
        category="beauty",
    ),
    Product(
        title="Wireless Noise Cancelling Headphones",
        raw_specs="Connectivity: Bluetooth 5.3, Feature: Active Noise Cancelling, "
        "Battery: 40 hours, Charging: USB-C Fast Charging, Rating: Water resistant",
        sku="HPN-NC-003",
        category="home",
    ),
]


def show(pipeline: CatalogPipeline, product: Product) -> None:
    enriched = pipeline.enrich(product)
    print("=" * 72)
    print(f"PRODUCT: {product.title}  [{product.category}]")
    print("=" * 72)

    print("STEP 1  SEO ENRICHMENT")
    print(f"  SEO title    : {enriched.seo_title}")
    print("  Top keywords :")
    for kw in enriched.keywords[:5]:
        print(f"    - {kw.keyword:<38} vol={kw.volume:>6}  relevance={kw.relevance:.2f}")

    print("\nSTEP 2  FEATURE-TO-BENEFIT CONVERSION")
    for benefit in enriched.benefits:
        print(f"    {benefit.feature_key} = {benefit.feature_value}")
        print(f"      -> {benefit.text}")

    print("\nSTEP 3  PLATFORM CONTEXTUALIZATION (Amazon)")
    print(json.dumps(pipeline.render(enriched, "amazon"), indent=2, ensure_ascii=False))
    print()


def main() -> None:
    pipeline = CatalogPipeline()
    for product in PRODUCTS:
        show(pipeline, product)


if __name__ == "__main__":
    main()
