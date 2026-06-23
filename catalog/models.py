"""Core data models for the Multi-Channel Catalog Scaling pipeline.

These dataclasses are the contract that flows between the three pipeline
stages. Keeping them small and explicit makes each stage independently
testable and lets new destination platforms be added without touching the
enrichment logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Product:
    """Raw product input as it arrives from the source catalog/PIM."""

    title: str
    raw_specs: str = ""
    description: str = ""
    sku: str = ""
    category: str = ""  # optional; when set, keyword matching is scoped to it

    def search_text(self) -> str:
        """Text used for keyword matching: title + description + specs."""
        return " ".join(part for part in (self.title, self.description, self.raw_specs) if part)


@dataclass
class KeywordMatch:
    """A scraped keyword that is relevant to a product."""

    keyword: str
    volume: int
    relevance: float  # 0..1 fraction of keyword terms found in the product text

    @property
    def score(self) -> float:
        """Ranking score combining demand (volume) and fit (relevance)."""
        return self.volume * self.relevance


@dataclass
class Benefit:
    """A customer-facing benefit derived from a single technical feature."""

    feature_key: str
    feature_value: str
    text: str
    tags: List[str] = field(default_factory=list)


@dataclass
class EnrichedProduct:
    """Output of the enrichment stages, ready for platform formatting."""

    product: Product
    keywords: List[KeywordMatch] = field(default_factory=list)
    specs: Dict[str, str] = field(default_factory=dict)
    benefits: List[Benefit] = field(default_factory=list)
    seo_title: str = ""

    def top_keywords(self, limit: int = 5) -> List[str]:
        return [k.keyword for k in self.keywords[:limit]]
