#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Manual smoke test for CUHK scraping and lookup.

Run from repository root:

```bash
source .venv/bin/activate
python test/cuhk_scrape_smoke.py
```

For a full build:

```bash
source .venv/bin/activate
python test/cuhk_scrape_smoke.py --full
```
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.multilang.cmn_yue.dictionaries import LookupDirection
from scinoephile.multilang.cmn_yue.dictionaries.cuhk import (
    CuhkDictionaryBuilder,
    CuhkDictionaryService,
)


def get_argparser() -> ArgumentParser:
    """Get command-line argument parser.

    Returns:
        configured argument parser
    """
    parser = ArgumentParser(
        description="Manual smoke test for CUHK dictionary scraping/build/lookup."
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".cache/cuhk-smoke"),
        help="Cache directory for scraped HTML and sqlite database.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=5,
        help="How many discovered links to scrape in smoke mode.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="巴士",
        help="Lookup query to run after build.",
    )
    parser.add_argument(
        "--direction",
        type=LookupDirection,
        choices=list(LookupDirection),
        default=LookupDirection.MANDARIN_TO_CANTONESE,
        help="Lookup direction.",
    )
    parser.add_argument(
        "--min-delay-seconds",
        type=float,
        default=0.0,
        help="Minimum delay between HTTP requests.",
    )
    parser.add_argument(
        "--max-delay-seconds",
        type=float,
        default=0.0,
        help="Maximum delay between HTTP requests.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Maximum retries per HTTP request.",
    )
    parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=20.0,
        help="Per-request timeout.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full build instead of limited smoke scrape.",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild when --full is selected.",
    )
    return parser


def run_smoke(
    cache_dir_path: Path,
    sample_size: int,
    min_delay_seconds: float,
    max_delay_seconds: float,
    max_retries: int,
    request_timeout_seconds: float,
    query: str,
    direction: LookupDirection,
):
    """Run limited smoke scrape/build/lookup.

    Arguments:
        cache_dir_path: cache directory path
        sample_size: number of links to scrape
        min_delay_seconds: minimum delay between requests
        max_delay_seconds: maximum delay between requests
        max_retries: maximum retries per request
        request_timeout_seconds: request timeout
        query: lookup query
        direction: lookup direction
    """
    builder = CuhkDictionaryBuilder(
        cache_dir_path=cache_dir_path,
        min_delay_seconds=min_delay_seconds,
        max_delay_seconds=max_delay_seconds,
        max_retries=max_retries,
        request_timeout_seconds=request_timeout_seconds,
    )

    print(f"[1/5] Discovering links from {builder.cache_dir_path}")
    links = builder.links.discover_word_links()
    print(f"Discovered {len(links)} link(s)")
    if links:
        print(f"First link: {links[0]}")

    subset_count = max(1, sample_size)
    subset = links[:subset_count]
    print(f"[2/5] Scraping {len(subset)} page(s)")
    builder.links.scrape_word_pages(subset, skip_existing=False)

    print("[3/5] Parsing scraped pages")
    entries = builder.parser.parse_scraped_pages()
    print(f"Parsed {len(entries)} entry(ies)")

    print("[4/5] Writing sqlite database")
    builder.writer.write_database(entries)
    print(f"Database path: {builder.database_path}")

    print("[5/5] Running lookup")
    service = CuhkDictionaryService(cache_dir_path=cache_dir_path)
    results = service.lookup(query=query, direction=direction, limit=3)
    print(f"Lookup returned {len(results)} result(s)")
    if results:
        top = results[0]
        print(
            "Top result: "
            f"trad={top.traditional} simp={top.simplified} "
            f"jyutping={top.jyutping} pinyin={top.pinyin}"
        )


def run_full(
    cache_dir_path: Path,
    min_delay_seconds: float,
    max_delay_seconds: float,
    max_retries: int,
    request_timeout_seconds: float,
    force_rebuild: bool,
):
    """Run full CUHK build.

    Arguments:
        cache_dir_path: cache directory path
        min_delay_seconds: minimum delay between requests
        max_delay_seconds: maximum delay between requests
        max_retries: maximum retries per request
        request_timeout_seconds: request timeout
        force_rebuild: whether to force rebuild
    """
    service = CuhkDictionaryService(
        cache_dir_path=cache_dir_path,
        auto_build_missing=False,
        min_delay_seconds=min_delay_seconds,
        max_delay_seconds=max_delay_seconds,
    )
    service.builder.max_retries = max_retries
    service.builder.request_timeout_seconds = request_timeout_seconds

    print("Running full CUHK build. This may take a long time.")
    database_path = service.build(force_rebuild=force_rebuild)
    print(f"Build completed: {database_path}")


def main():
    """Execute CLI entry point."""
    args = get_argparser().parse_args()
    cache_dir_path = args.cache_dir.resolve()

    print(f"Using cache directory: {cache_dir_path}")
    if args.full:
        run_full(
            cache_dir_path=cache_dir_path,
            min_delay_seconds=args.min_delay_seconds,
            max_delay_seconds=args.max_delay_seconds,
            max_retries=args.max_retries,
            request_timeout_seconds=args.request_timeout_seconds,
            force_rebuild=args.force_rebuild,
        )
    else:
        run_smoke(
            cache_dir_path=cache_dir_path,
            sample_size=args.sample_size,
            min_delay_seconds=args.min_delay_seconds,
            max_delay_seconds=args.max_delay_seconds,
            max_retries=args.max_retries,
            request_timeout_seconds=args.request_timeout_seconds,
            query=args.query,
            direction=args.direction,
        )


if __name__ == "__main__":
    main()
