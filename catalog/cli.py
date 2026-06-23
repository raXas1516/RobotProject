"""Command-line entry point for the catalog pipeline.

Examples:
    python -m catalog.cli \
        --title "Stainless Steel Rose Gold Pendant" \
        --specs "Material: 316L Stainless Steel, Coating: 18k Rose Gold PVD" \
        --platform amazon shopify ebay

    # Or pipe a product as JSON on stdin:
    echo '{"title": "...", "raw_specs": "..."}' | python -m catalog.cli --json
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .models import Product
from .pipeline import CatalogPipeline
from .platforms import available_platforms


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-Channel Catalog Scaling pipeline")
    parser.add_argument("--title", help="Product title")
    parser.add_argument("--specs", default="", help="Raw technical spec string")
    parser.add_argument("--description", default="", help="Optional existing description")
    parser.add_argument("--sku", default="", help="Optional SKU")
    parser.add_argument(
        "--platform",
        nargs="+",
        default=None,
        metavar="NAME",
        help=f"Target platform(s): {', '.join(available_platforms())} (default: all)",
    )
    parser.add_argument("--json", action="store_true", help="Read a product as JSON from stdin")
    parser.add_argument("--min-relevance", type=float, default=0.5, help="Keyword match threshold (0-1)")
    return parser.parse_args(argv)


def _build_product(args: argparse.Namespace) -> Product:
    if args.json:
        data = json.load(sys.stdin)
        return Product(
            title=data["title"],
            raw_specs=data.get("raw_specs", data.get("specs", "")),
            description=data.get("description", ""),
            sku=data.get("sku", ""),
        )
    if not args.title:
        raise SystemExit("error: --title is required (or use --json)")
    return Product(title=args.title, raw_specs=args.specs, description=args.description, sku=args.sku)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    product = _build_product(args)
    pipeline = CatalogPipeline()
    listings = pipeline.run(product, platforms=args.platform, min_relevance=args.min_relevance)
    print(json.dumps(listings, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
