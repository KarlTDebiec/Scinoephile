#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for listing cache entries."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, TypedDict, Unpack

from scinoephile.common.argument_parsing import get_arg_groups_by_name
from scinoephile.core.cache.operations import (
    get_default_cache_dir_path,
    list_entries,
)
from scinoephile.core.cli import ScinoephileCliBase

__all__ = ["CacheListCli"]

_SORT_CHOICES = ["name", "size", "mtime", "atime"]
_FORMAT_CHOICES = ["text", "json", "jsonl"]


class _CacheListCliKwargs(TypedDict, total=False):
    """Keyword arguments for CacheListCli."""

    cache_dir: Path | None
    """Cache root directory."""
    namespace: str | None
    """Optional namespace filter."""
    limit: int | None
    """Maximum number of entries to show."""
    sort: str
    """Sort field."""
    reverse: bool
    """Whether to reverse sort order."""
    format: str
    """Output format."""


class CacheListCli(ScinoephileCliBase):
    """List cache entries discovered under the cache root."""

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
            help="limit listing to one namespace",
        )
        arg_groups["operation arguments"].add_argument(
            "--limit",
            default=None,
            dest="limit",
            metavar="N",
            type=int,
            help="maximum number of entries to show",
        )
        arg_groups["operation arguments"].add_argument(
            "--sort",
            choices=_SORT_CHOICES,
            default="name",
            dest="sort",
            help="sort field (default: name)",
        )
        arg_groups["operation arguments"].add_argument(
            "--reverse",
            action="store_true",
            default=False,
            dest="reverse",
            help="reverse sort order",
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
        return "list"

    @classmethod
    def _main(cls, **kwargs: Unpack[_CacheListCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        cache_dir = kwargs.pop("cache_dir") or get_default_cache_dir_path()
        namespace = kwargs.pop("namespace")
        limit = kwargs.pop("limit")
        sort = kwargs.pop("sort", "name")
        reverse = kwargs.pop("reverse", False)
        fmt = kwargs.pop("format", "text")

        try:
            entries = list_entries(
                cache_dir,
                namespace=namespace,
                limit=limit,
                sort=sort,
                reverse=reverse,
            )
        except ValueError as exc:
            print(f"Error: {exc}")
            return

        if fmt == "json":
            rows = [_entry_to_dict(e) for e in entries]
            print(json.dumps(rows, indent=2))
        elif fmt == "jsonl":
            for entry in entries:
                print(json.dumps(_entry_to_dict(entry)))
        else:
            if not entries:
                print("No cache entries found.")
                return
            for entry in entries:
                mtime_str = _format_timestamp(entry.mtime)
                size_str = _format_size(entry.size)
                print(
                    f"{entry.namespace}/{entry.rel_path}"
                    f"  size={size_str}"
                    f"  mtime={mtime_str}"
                    f"  files={entry.file_count}"
                )


def _entry_to_dict(entry: object) -> dict[str, object]:
    """Convert a CacheEntry to a JSON-serialisable dict.

    Arguments:
        entry: cache entry
    Returns:
        JSON-serialisable dictionary
    """
    from scinoephile.core.cache.entry import CacheEntry

    assert isinstance(entry, CacheEntry)
    return {
        "namespace": entry.namespace,
        "rel_path": str(entry.rel_path),
        "size": entry.size,
        "mtime": entry.mtime,
        "atime": entry.atime,
        "file_count": entry.file_count,
    }


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


def _format_timestamp(ts: float) -> str:
    """Format a POSIX timestamp as an ISO 8601 string (UTC).

    Arguments:
        ts: POSIX timestamp
    Returns:
        formatted timestamp string
    """
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    CacheListCli.main()
