#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for displaying cache statistics."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, TypedDict, Unpack

from scinoephile.common.argument_parsing import get_arg_groups_by_name
from scinoephile.core.cache.operations import get_default_cache_dir_path, get_stats
from scinoephile.core.cli import ScinoephileCliBase

__all__ = ["CacheStatsCli"]

_FORMAT_CHOICES = ["text", "json"]


class _CacheStatsCliKwargs(TypedDict, total=False):
    """Keyword arguments for CacheStatsCli."""

    cache_dir: Path | None
    """Cache root directory."""
    namespace: str | None
    """Optional namespace filter."""
    format: str
    """Output format."""


class CacheStatsCli(ScinoephileCliBase):
    """Show aggregate statistics for the cache."""

    localizations: ClassVar[dict[str, dict[str, str]]] = {}
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(
            parser,
            "operation arguments",
            optional_arguments_name="additional arguments",
        )

        arg_groups["operation arguments"].add_argument(
            "--cache-dir",
            default=None,
            dest="cache_dir",
            metavar="PATH",
            type=Path,
            help="cache root directory to inspect (default: OS-appropriate cache path)",
        )
        arg_groups["operation arguments"].add_argument(
            "--namespace",
            default=None,
            dest="namespace",
            metavar="NAME",
            type=str,
            help="limit stats to one namespace",
        )
        arg_groups["operation arguments"].add_argument(
            "--format",
            choices=_FORMAT_CHOICES,
            default="text",
            dest="format",
            help="output format (default: text)",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "stats"

    @classmethod
    def _main(cls, **kwargs: Unpack[_CacheStatsCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        cache_dir = kwargs.pop("cache_dir") or get_default_cache_dir_path()
        namespace = kwargs.pop("namespace")
        fmt = kwargs.pop("format", "text")

        try:
            stats = get_stats(cache_dir, namespace=namespace)
        except ValueError as exc:
            print(f"Error: {exc}")
            return

        if fmt == "json":
            print(json.dumps(stats, indent=2))
        else:
            ns_stats: list[dict] = stats["namespaces"]  # type: ignore[assignment]
            total: dict = stats["total"]  # type: ignore[assignment]
            if not ns_stats:
                print("No cache entries found.")
                return
            for ns in ns_stats:
                oldest_mtime = _fmt_ts(ns["oldest_mtime"])
                newest_mtime = _fmt_ts(ns["newest_mtime"])
                size_str = _format_size(ns["size"])
                print(
                    f"namespace: {ns['namespace']}"
                    f"  entries: {ns['count']}"
                    f"  size: {size_str}"
                    f"  oldest: {oldest_mtime}"
                    f"  newest: {newest_mtime}"
                )
            total_size_str = _format_size(total["size"])
            print(f"total:  entries: {total['count']}  size: {total_size_str}")


def _fmt_ts(ts: float | None) -> str:
    """Format an optional POSIX timestamp as an ISO 8601 string.

    Arguments:
        ts: POSIX timestamp, or None
    Returns:
        formatted string or '-' if None
    """
    if ts is None:
        return "-"
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _format_size(size: int) -> str:
    """Format a byte count as a human-readable string.

    Arguments:
        size: size in bytes
    Returns:
        human-readable size string
    """
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size //= 1024
    return f"{size:.1f} TB"


if __name__ == "__main__":
    CacheStatsCli.main()
