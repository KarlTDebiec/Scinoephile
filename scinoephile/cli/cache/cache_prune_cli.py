#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for pruning old cache entries."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import ClassVar, TypedDict, Unpack

from scinoephile.common.argument_parsing import get_arg_groups_by_name
from scinoephile.core.cache.duration import parse_duration
from scinoephile.core.cache.operations import get_default_cache_dir_path, prune_entries
from scinoephile.core.cli import ScinoephileCliBase

__all__ = ["CachePruneCli"]


class _CachePruneCliKwargs(TypedDict, total=False):
    """Keyword arguments for CachePruneCli."""

    cache_dir: Path | None
    """Cache root directory."""
    namespace: str | None
    """Optional namespace filter."""
    older_than: str
    """Delete entries older than this duration."""
    dry_run: bool
    """Whether to preview deletions without deleting."""
    yes: bool
    """Explicit confirmation required for destructive deletion."""


class CachePruneCli(ScinoephileCliBase):
    """Delete cache entries older than a given duration."""

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
            help="cache root directory (default: OS-appropriate cache path)",
        )
        arg_groups["operation arguments"].add_argument(
            "--namespace",
            default=None,
            dest="namespace",
            metavar="NAME",
            type=str,
            help="limit pruning to one namespace",
        )
        arg_groups["operation arguments"].add_argument(
            "--older-than",
            required=True,
            dest="older_than",
            metavar="DURATION",
            type=str,
            help=(
                "delete entries older than this duration "
                "(e.g. '7d', '12h', '30m', '1w')"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            dest="dry_run",
            help="show what would be deleted without deleting",
        )
        arg_groups["operation arguments"].add_argument(
            "--yes",
            action="store_true",
            default=False,
            dest="yes",
            help="confirm deletion (required unless --dry-run is specified)",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "prune"

    @classmethod
    def _main(cls, **kwargs: Unpack[_CachePruneCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        parser = cls.argparser()
        cache_dir = kwargs.pop("cache_dir") or get_default_cache_dir_path()
        namespace = kwargs.pop("namespace")
        older_than_str = kwargs.pop("older_than")
        dry_run = kwargs.pop("dry_run", False)
        yes = kwargs.pop("yes", False)

        if not dry_run and not yes:
            parser.error(
                "Refusing to delete without --yes. "
                "Use --dry-run to preview, or add --yes to confirm deletion."
            )

        try:
            older_than = parse_duration(older_than_str)
        except ValueError as exc:
            parser.error(str(exc))

        try:
            entries = prune_entries(
                cache_dir,
                older_than=older_than,
                namespace=namespace,
                dry_run=dry_run,
            )
        except ValueError as exc:
            print(f"Error: {exc}")
            return

        if not entries:
            print("No entries to prune.")
            return

        label = "[dry-run] would delete" if dry_run else "deleted"
        for entry in entries:
            print(f"{label}: {entry.namespace}/{entry.rel_path}")
        print(f"{label.split(':', maxsplit=1)[0].strip()}: {len(entries)} entries total.")


if __name__ == "__main__":
    CachePruneCli.main()
