"""Step 2 - Feature-to-Benefit Conversion.

Parses a raw technical spec string into structured key/value features, then
maps each feature to a compelling customer-facing benefit using a rule-based
knowledge base. The converter is intentionally pluggable: swap in an
LLM-backed implementation by subclassing and overriding `benefit_for`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import Benefit

_DEFAULT_RULES = Path(__file__).parent / "data" / "benefit_rules.json"


def parse_specs(raw: str) -> Dict[str, str]:
    """Parse "Material: 316L Steel, Coating: 18k Rose Gold PVD" into a dict.

    Accepts ',' or ';' between pairs and ':' or '=' between key and value.
    Pairs without a separator are kept under a numbered "feature" key so no
    information is silently dropped.
    """
    specs: Dict[str, str] = {}
    if not raw:
        return specs
    parts = [p.strip() for chunk in raw.split(";") for p in chunk.split(",")]
    unlabeled = 0
    for part in parts:
        if not part:
            continue
        sep = ":" if ":" in part else ("=" if "=" in part else None)
        if sep:
            key, value = part.split(sep, 1)
            key, value = key.strip(), value.strip()
            if key and value:
                specs[key] = value
                continue
        unlabeled += 1
        specs[f"feature {unlabeled}"] = part
    return specs


class FeatureBenefitConverter:
    """Maps technical features to benefits via a prioritised rule base."""

    def __init__(self, rules: List[dict], fallback_template: str = ""):
        # Highest priority first so the strongest benefit wins per feature.
        self._rules = sorted(rules, key=lambda r: r.get("priority", 0), reverse=True)
        self._fallback_template = fallback_template

    @classmethod
    def from_file(cls, path: Path | str = _DEFAULT_RULES) -> "FeatureBenefitConverter":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(data["rules"], data.get("fallback_template", ""))

    @staticmethod
    def _matches(rule: dict, key: str, value: str) -> bool:
        match = rule.get("match", {})
        key_l, value_l = key.lower(), value.lower()
        if "key_contains" in match and match["key_contains"].lower() not in key_l:
            return False
        if "value_contains" in match and match["value_contains"].lower() not in value_l:
            return False
        # text_contains matches against "key value" so attribute-style specs
        # (e.g. "Waterproof: Yes") and descriptive values both work.
        if "text_contains" in match and match["text_contains"].lower() not in f"{key_l} {value_l}":
            return False
        # An empty match block never matches (avoids accidental catch-all rules).
        return bool(match)

    def benefit_for(self, key: str, value: str) -> Optional[Benefit]:
        """Return the best benefit for a single feature, or a fallback."""
        for rule in self._rules:
            if self._matches(rule, key, value):
                return Benefit(
                    feature_key=key,
                    feature_value=value,
                    text=rule["benefit"],
                    tags=list(rule.get("tags", [])),
                )
        if self._fallback_template:
            text = self._fallback_template.format(key_lower=key.lower(), value=value, key=key)
            return Benefit(feature_key=key, feature_value=value, text=text, tags=["generic"])
        return None

    def convert(self, specs: Dict[str, str]) -> List[Benefit]:
        """Convert all parsed specs into a de-duplicated benefit list."""
        benefits: List[Benefit] = []
        seen_texts = set()
        for key, value in specs.items():
            benefit = self.benefit_for(key, value)
            if benefit and benefit.text not in seen_texts:
                benefits.append(benefit)
                seen_texts.add(benefit.text)
        return benefits
