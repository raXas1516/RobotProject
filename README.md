# RobotProject

This repository contains two independent pieces of work:

- **`pirobocode.py`** — the original Raspberry Pi / Arduino robot controller (Flask + nanpy).
- **`catalog/`** — the **Multi-Channel Catalog Scaling** system (documented below).

---

## Multi-Channel Catalog Scaling

Clean, modular infrastructure that turns a single raw product into
channel-ready marketplace listings through a three-stage pipeline.

```
Product ──▶ Step 1: SEO Enrichment ──▶ Step 2: Feature-to-Benefit ──▶ EnrichedProduct ──▶ Step 3: Platform Contextualization ──▶ listings
```

### The three steps

| Step | Module | What it does |
|------|--------|--------------|
| **1. SEO Enrichment** | `catalog/seo.py` | Cross-references the product title against a list of scraped high-volume Google/Amazon keywords, ranks them by `volume × relevance`, and weaves the best missing keyword into an SEO title. |
| **2. Feature-to-Benefit** | `catalog/benefits.py` | Parses raw technical specs (`"Material: 316L Stainless Steel, Coating: 18k Rose Gold PVD"`) into structured fields, then maps each feature to a compelling customer benefit via a prioritised rule base. |
| **3. Platform Contextualization** | `catalog/platforms.py` | Formats the enriched product exactly how each destination marketplace wants it — Amazon bullet points, clean Shopify HTML, or concise eBay item specifics. |

### Quick start

```python
from catalog import CatalogPipeline, Product

pipeline = CatalogPipeline()
listings = pipeline.run(
    Product(
        title="Stainless Steel Rose Gold Pendant",
        raw_specs="Material: 316L Stainless Steel, Coating: 18k Rose Gold PVD, Waterproof: Yes",
    ),
    platforms=["amazon", "shopify", "ebay"],
)
print(listings["amazon"]["bullet_points"])
```

### Command line

```bash
# From explicit args
python -m catalog.cli \
    --title "Stainless Steel Rose Gold Pendant" \
    --specs "Material: 316L Stainless Steel, Coating: 18k Rose Gold PVD" \
    --platform amazon shopify ebay

# Or pipe a product as JSON
echo '{"title": "...", "raw_specs": "..."}' | python -m catalog.cli --json
```

### Runnable demo

```bash
python examples/run_example.py
```

### Project layout

```
catalog/
├── __init__.py          # public API
├── models.py            # Product, EnrichedProduct, KeywordMatch, Benefit
├── seo.py               # Step 1 — SEOEnricher
├── benefits.py          # Step 2 — FeatureBenefitConverter + parse_specs
├── platforms.py         # Step 3 — Amazon / Shopify / eBay formatters
├── pipeline.py          # CatalogPipeline (orchestration)
├── cli.py               # command-line entry point
└── data/
    ├── keywords.json        # scraped keyword volumes (refreshable)
    └── benefit_rules.json   # feature → benefit knowledge base
examples/run_example.py
tests/test_pipeline.py
```

### Extending the system

- **New keywords / benefits** — edit the JSON files in `catalog/data/`; no code change required.
- **New marketplace** — add a `PlatformFormatter` subclass in `catalog/platforms.py` and register it. Enrichment stages are untouched.
- **LLM-backed benefits** — the rule-based `FeatureBenefitConverter` is pluggable; subclass it and override `benefit_for()` to call an LLM while keeping the rest of the pipeline identical.

### Tests

```bash
python -m unittest discover -s tests -v
```

All stages are covered by unit tests (spec parsing, keyword ranking, benefit
priority/fallback, and per-platform formatting constraints).
