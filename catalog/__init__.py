"""Multi-Channel Catalog Scaling.

A clean, modular pipeline that turns a raw product into channel-ready
listings in three stages:

    1. SEO Enrichment            (catalog.seo)
    2. Feature-to-Benefit        (catalog.benefits)
    3. Platform Contextualization(catalog.platforms)

Typical use:

    from catalog import CatalogPipeline, Product

    pipeline = CatalogPipeline()
    listings = pipeline.run(
        Product(
            title="Stainless Steel Rose Gold Pendant",
            raw_specs="Material: 316L Stainless Steel, Coating: 18k Rose Gold PVD",
        ),
        platforms=["amazon", "shopify", "ebay"],
    )
"""

from .benefits import FeatureBenefitConverter, parse_specs
from .models import Benefit, EnrichedProduct, KeywordMatch, Product
from .pipeline import CatalogPipeline
from .platforms import available_platforms, get_formatter
from .seo import SEOEnricher

__all__ = [
    "CatalogPipeline",
    "Product",
    "EnrichedProduct",
    "KeywordMatch",
    "Benefit",
    "SEOEnricher",
    "FeatureBenefitConverter",
    "parse_specs",
    "get_formatter",
    "available_platforms",
]
