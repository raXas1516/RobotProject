"""Unit tests for the Multi-Channel Catalog Scaling pipeline.

Run from the repo root:  python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from catalog import CatalogPipeline, Product, SEOEnricher  # noqa: E402
from catalog.benefits import FeatureBenefitConverter, parse_specs  # noqa: E402
from catalog.platforms import get_formatter  # noqa: E402


class SpecParsingTests(unittest.TestCase):
    def test_parses_colon_and_comma(self):
        specs = parse_specs("Material: 316L Stainless Steel, Coating: 18k Rose Gold PVD")
        self.assertEqual(specs["Material"], "316L Stainless Steel")
        self.assertEqual(specs["Coating"], "18k Rose Gold PVD")

    def test_handles_equals_and_semicolon(self):
        specs = parse_specs("Color = Rose Gold; Waterproof = Yes")
        self.assertEqual(specs["Color"], "Rose Gold")
        self.assertEqual(specs["Waterproof"], "Yes")

    def test_unlabeled_feature_preserved(self):
        specs = parse_specs("Premium gift box included")
        self.assertEqual(specs["feature 1"], "Premium gift box included")

    def test_empty_string(self):
        self.assertEqual(parse_specs(""), {})


class SEOTests(unittest.TestCase):
    def setUp(self):
        self.seo = SEOEnricher.from_file()

    def test_matches_relevant_keywords(self):
        product = Product(title="Stainless Steel Rose Gold Pendant")
        matches = self.seo.match_keywords(product)
        self.assertTrue(matches)
        # Results are ranked by volume * relevance, descending.
        scores = [m.score for m in matches]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_seo_title_adds_keyword(self):
        product = Product(title="Stainless Steel Rose Gold Pendant")
        enriched = self.seo.enrich(product)
        self.assertTrue(enriched.seo_title.startswith(product.title))

    def test_irrelevant_product_gets_no_matches(self):
        product = Product(title="Wooden Garden Bench")
        self.assertEqual(self.seo.match_keywords(product), [])

    def test_category_scopes_keyword_matches(self):
        # A beauty product should only match beauty keywords, not jewelry ones
        # that happen to share generic tokens.
        product = Product(title="Brightening Vitamin C Face Serum", category="beauty")
        matches = self.seo.match_keywords(product)
        self.assertTrue(matches)
        self.assertTrue(any("vitamin c" in m.keyword for m in matches))
        # No jewelry keyword should leak into a beauty product's matches.
        self.assertFalse(any("necklace" in m.keyword or "ring" in m.keyword for m in matches))

    def test_no_category_searches_all(self):
        # Backward compatible: with no category set, the full pool is searched.
        product = Product(title="Stainless Steel Rose Gold Pendant")
        self.assertTrue(self.seo.match_keywords(product))


class BenefitTests(unittest.TestCase):
    def setUp(self):
        self.converter = FeatureBenefitConverter.from_file()

    def test_316l_maps_to_durability_benefit(self):
        benefit = self.converter.benefit_for("Material", "316L Stainless Steel")
        self.assertIsNotNone(benefit)
        self.assertIn("316L", benefit.text)
        self.assertIn("durability", benefit.tags)

    def test_priority_picks_strongest_rule(self):
        # "316L Stainless Steel" matches both the 316l rule (p100) and the
        # generic stainless-steel rule (p60); the higher priority must win.
        benefit = self.converter.benefit_for("Material", "316L Stainless Steel")
        self.assertIn("Surgical-grade", benefit.text)

    def test_text_contains_matches_on_key(self):
        # "Waterproof: Yes" carries the signal in the key, not the value.
        benefit = self.converter.benefit_for("Waterproof", "Yes")
        self.assertIsNotNone(benefit)
        self.assertIn("waterproof", benefit.text.lower())

    def test_fallback_used_for_unknown_feature(self):
        benefit = self.converter.benefit_for("Origin", "Italy")
        self.assertIsNotNone(benefit)
        self.assertIn("Italy", benefit.text)

    def test_cross_category_benefits(self):
        # Spot-check the expanded multi-category knowledge base.
        cases = {
            ("Active", "Vitamin C 15%"): "vitamin c",
            ("Hydration", "Hyaluronic Acid"): "hyaluronic acid",
            ("Material", "Merino Wool"): "merino wool",
            ("Feature", "Active Noise Cancelling"): "noise cancellation",
            ("Battery", "40 hours"): "battery",
        }
        for (key, value), expected in cases.items():
            benefit = self.converter.benefit_for(key, value)
            self.assertIsNotNone(benefit, f"{key}={value} produced no benefit")
            self.assertIn(expected, benefit.text.lower(), f"{key}={value}")

    def test_convert_dedupes(self):
        specs = {"a": "316L Stainless Steel", "b": "316L Stainless Steel"}
        benefits = self.converter.convert(specs)
        self.assertEqual(len(benefits), 1)


class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.pipeline = CatalogPipeline()
        self.product = Product(
            title="Stainless Steel Rose Gold Pendant",
            raw_specs="Material: 316L Stainless Steel, Coating: 18k Rose Gold PVD, Waterproof: Yes",
        )
        self.enriched = self.pipeline.enrich(self.product)

    def test_amazon_bullets_capped_at_five(self):
        out = self.pipeline.render(self.enriched, "amazon")
        self.assertLessEqual(len(out["bullet_points"]), 5)
        self.assertTrue(out["search_terms"])

    def test_ebay_title_within_80_chars(self):
        out = self.pipeline.render(self.enriched, "ebay")
        self.assertLessEqual(len(out["title"]), 80)
        self.assertIn("Material", out["item_specifics"])

    def test_shopify_produces_html(self):
        out = self.pipeline.render(self.enriched, "shopify")
        self.assertIn("<ul>", out["body_html"])
        self.assertIn("<table>", out["body_html"])
        self.assertLessEqual(len(out["meta_description"]), 160)

    def test_unknown_platform_raises(self):
        with self.assertRaises(ValueError):
            get_formatter("myspace")

    def test_run_all_platforms(self):
        listings = self.pipeline.run(self.product)
        self.assertEqual(set(listings), {"amazon", "shopify", "ebay"})


if __name__ == "__main__":
    unittest.main()
