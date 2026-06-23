"""Step 3 - Platform Contextualization.

Formats an EnrichedProduct exactly the way each destination marketplace
expects. Each formatter implements `PlatformFormatter` so adding a new
channel (Etsy, Walmart, TikTok Shop ...) is a single new class plus a
registry entry - no changes to the enrichment stages.
"""

from __future__ import annotations

import html
from abc import ABC, abstractmethod
from typing import Dict, List, Type

from .models import EnrichedProduct


class PlatformFormatter(ABC):
    """Renders an enriched product into a platform-specific listing."""

    name: str
    title_max_len: int = 200

    @abstractmethod
    def format(self, enriched: EnrichedProduct) -> Dict[str, object]:
        """Return a dict of platform fields ready to publish."""

    def _title(self, enriched: EnrichedProduct) -> str:
        title = enriched.seo_title or enriched.product.title
        return title[: self.title_max_len].rstrip(" |").rstrip()


class AmazonFormatter(PlatformFormatter):
    """Amazon: keyword-rich title, 5 benefit bullets, backend search terms."""

    name = "amazon"
    title_max_len = 200

    def format(self, enriched: EnrichedProduct) -> Dict[str, object]:
        bullets = [b.text for b in enriched.benefits][:5]
        # Backend search terms exclude words already in the title (Amazon ignores dupes).
        title_words = set(self._title(enriched).lower().split())
        search_terms: List[str] = []
        for kw in enriched.keywords:
            for word in kw.keyword.lower().split():
                if word not in title_words and word not in search_terms:
                    search_terms.append(word)
        return {
            "title": self._title(enriched),
            "bullet_points": bullets,
            "search_terms": " ".join(search_terms[:25]),
        }


class ShopifyFormatter(PlatformFormatter):
    """Shopify: clean semantic HTML body plus SEO meta fields."""

    name = "shopify"
    title_max_len = 255

    def format(self, enriched: EnrichedProduct) -> Dict[str, object]:
        parts: List[str] = []
        if enriched.benefits:
            items = "".join(f"<li>{html.escape(b.text)}</li>" for b in enriched.benefits)
            parts.append("<h3>Why you'll love it</h3>")
            parts.append(f"<ul>{items}</ul>")
        if enriched.specs:
            rows = "".join(
                f"<tr><th>{html.escape(k)}</th><td>{html.escape(v)}</td></tr>"
                for k, v in enriched.specs.items()
            )
            parts.append("<h3>Specifications</h3>")
            parts.append(f"<table>{rows}</table>")
        body_html = "\n".join(parts)
        meta = enriched.benefits[0].text if enriched.benefits else enriched.product.title
        return {
            "title": self._title(enriched),
            "body_html": body_html,
            "meta_description": meta[:160],
            "tags": enriched.top_keywords(8),
        }


class EbayFormatter(PlatformFormatter):
    """eBay: short title (80 char cap), item specifics, concise description."""

    name = "ebay"
    title_max_len = 80

    def format(self, enriched: EnrichedProduct) -> Dict[str, object]:
        description = " ".join(b.text for b in enriched.benefits[:3])
        return {
            "title": self._title(enriched),
            "item_specifics": dict(enriched.specs),
            "description": description,
        }


_REGISTRY: Dict[str, Type[PlatformFormatter]] = {
    AmazonFormatter.name: AmazonFormatter,
    ShopifyFormatter.name: ShopifyFormatter,
    EbayFormatter.name: EbayFormatter,
}


def available_platforms() -> List[str]:
    return sorted(_REGISTRY)


def get_formatter(platform: str) -> PlatformFormatter:
    key = platform.lower().strip()
    if key not in _REGISTRY:
        raise ValueError(f"Unknown platform '{platform}'. Available: {', '.join(available_platforms())}")
    return _REGISTRY[key]()
