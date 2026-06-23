"""Runnable demo of the Multi-Channel Catalog Scaling pipeline.

Run from the repo root:  python examples/run_example.py
"""

import json
import os
import sys

# Allow running directly without installing the package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from catalog import CatalogPipeline, Product  # noqa: E402


def main() -> None:
    product = Product(
        title="Stainless Steel Rose Gold Pendant",
        raw_specs="Material: 316L Stainless Steel, Coating: 18k Rose Gold PVD, "
        "Chain Length: 18 inches, Skin: Hypoallergenic, Waterproof: Yes",
        sku="PND-RG-001",
    )

    pipeline = CatalogPipeline()
    enriched = pipeline.enrich(product)

    print("=" * 70)
    print("STEP 1  SEO ENRICHMENT")
    print("=" * 70)
    print(f"Original title : {product.title}")
    print(f"SEO title      : {enriched.seo_title}")
    print("Top keywords   :")
    for kw in enriched.keywords[:5]:
        print(f"  - {kw.keyword:<32} vol={kw.volume:>6}  relevance={kw.relevance:.2f}")

    print("\n" + "=" * 70)
    print("STEP 2  FEATURE-TO-BENEFIT CONVERSION")
    print("=" * 70)
    for benefit in enriched.benefits:
        print(f"  {benefit.feature_key} = {benefit.feature_value}")
        print(f"    -> {benefit.text}")

    print("\n" + "=" * 70)
    print("STEP 3  PLATFORM CONTEXTUALIZATION")
    print("=" * 70)
    for platform in ("amazon", "shopify", "ebay"):
        print(f"\n--- {platform.upper()} ---")
        print(json.dumps(pipeline.render(enriched, platform), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
