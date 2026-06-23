"""Step 1 - SEO Enrichment.

Cross-references a product against a list of scraped high-volume search
keywords and produces ranked, relevant keywords plus an SEO-optimised title.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, List

from .models import EnrichedProduct, KeywordMatch, Product

_DEFAULT_KEYWORDS = Path(__file__).parent / "data" / "keywords.json"

# Words too generic to count toward keyword relevance.
_STOPWORDS = {"for", "the", "and", "with", "a", "an", "of", "to", "in"}


def _tokenize(text: str) -> List[str]:
    """Lowercase word tokens, stopwords removed."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS]


class SEOEnricher:
    """Matches products to scraped search keywords and builds SEO titles."""

    def __init__(self, keywords: Iterable[dict]):
        # Store as (keyword, volume, token_set) tuples for fast scoring.
        self._keywords = [
            (kw["keyword"], int(kw["volume"]), set(_tokenize(kw["keyword"])))
            for kw in keywords
            if kw.get("keyword")
        ]

    @classmethod
    def from_file(cls, path: Path | str = _DEFAULT_KEYWORDS) -> "SEOEnricher":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(data["keywords"])

    def match_keywords(self, product: Product, min_relevance: float = 0.5) -> List[KeywordMatch]:
        """Return keywords relevant to the product, ranked by demand x fit."""
        product_tokens = set(_tokenize(product.search_text()))
        matches: List[KeywordMatch] = []
        for keyword, volume, kw_tokens in self._keywords:
            if not kw_tokens:
                continue
            overlap = kw_tokens & product_tokens
            relevance = len(overlap) / len(kw_tokens)
            if relevance >= min_relevance:
                matches.append(KeywordMatch(keyword=keyword, volume=volume, relevance=relevance))
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches

    def build_seo_title(self, product: Product, keywords: List[KeywordMatch], max_len: int = 200) -> str:
        """Weave the highest-value keyword the title is missing into the title."""
        title = product.title.strip()
        title_tokens = set(_tokenize(title))
        for match in keywords:
            kw_tokens = set(_tokenize(match.keyword))
            # Only append a keyword that adds at least one new term.
            if kw_tokens - title_tokens:
                candidate = f"{title} | {match.keyword.title()}"
                if len(candidate) <= max_len:
                    return candidate
                break
        return title

    def enrich(self, product: Product, min_relevance: float = 0.5) -> EnrichedProduct:
        keywords = self.match_keywords(product, min_relevance=min_relevance)
        seo_title = self.build_seo_title(product, keywords)
        return EnrichedProduct(product=product, keywords=keywords, seo_title=seo_title)
