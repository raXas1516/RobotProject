"""Orchestrates the three Multi-Channel Catalog Scaling stages.

    Product --[SEO]--> --[Benefits]--> EnrichedProduct --[Platform]--> listing(s)
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .benefits import FeatureBenefitConverter, parse_specs
from .models import EnrichedProduct, Product
from .platforms import available_platforms, get_formatter
from .seo import SEOEnricher


class CatalogPipeline:
    """End-to-end pipeline: enrich a product and render it for any channel."""

    def __init__(
        self,
        seo: Optional[SEOEnricher] = None,
        converter: Optional[FeatureBenefitConverter] = None,
    ):
        self.seo = seo or SEOEnricher.from_file()
        self.converter = converter or FeatureBenefitConverter.from_file()

    def enrich(self, product: Product, min_relevance: float = 0.5) -> EnrichedProduct:
        """Run Step 1 (SEO) and Step 2 (benefits), producing an EnrichedProduct."""
        enriched = self.seo.enrich(product, min_relevance=min_relevance)
        enriched.specs = parse_specs(product.raw_specs)
        enriched.benefits = self.converter.convert(enriched.specs)
        return enriched

    def render(self, enriched: EnrichedProduct, platform: str) -> Dict[str, object]:
        """Run Step 3 (platform contextualization) for one platform."""
        return get_formatter(platform).format(enriched)

    def run(
        self,
        product: Product,
        platforms: Optional[List[str]] = None,
        min_relevance: float = 0.5,
    ) -> Dict[str, Dict[str, object]]:
        """Full pipeline: enrich once, then format for every requested platform."""
        enriched = self.enrich(product, min_relevance=min_relevance)
        targets = platforms or available_platforms()
        return {platform: self.render(enriched, platform) for platform in targets}
