#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for searching the CUHK dictionary cache."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from typing import TYPE_CHECKING, Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    int_arg,
    output_dir_arg,
)
from scinoephile.multilang.cmn_yue.dictionaries import LookupDirection
from scinoephile.multilang.cmn_yue.dictionaries.cuhk import CuhkDictionaryService

if TYPE_CHECKING:
    from scinoephile.multilang.cmn_yue.dictionaries import DictionaryEntry

logger = getLogger(__name__)


class CmnYueDictionarySearchCli(CommandLineInterface):
    """Command-line interface for searching the CUHK dictionary cache."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "search arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--cache-dir",
            metavar="DIR",
            default=None,
            type=output_dir_arg(),
            help="cache directory to use instead of the default CUHK data location",
        )

        # Operation arguments
        arg_groups["search arguments"].add_argument(
            "query",
            type=str,
            help="Mandarin or Cantonese query text",
        )
        arg_groups["search arguments"].add_argument(
            "--direction",
            type=LookupDirection,
            choices=list(LookupDirection),
            default=LookupDirection.MANDARIN_TO_CANTONESE,
            help="lookup direction",
        )
        arg_groups["search arguments"].add_argument(
            "--limit",
            metavar="N",
            type=int_arg(min_value=1),
            default=10,
            help="maximum number of matches to show",
        )

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        cache_dir_path = kwargs.pop("cache_dir")
        query = kwargs.pop("query")
        direction = kwargs.pop("direction")
        limit = kwargs.pop("limit")

        service = CuhkDictionaryService(
            cache_dir_path=cache_dir_path,
            auto_build_missing=False,
        )
        entries = service.lookup(query=query, direction=direction, limit=limit)
        cls._log_search_results(query, direction, entries)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "search"

    @classmethod
    def _log_search_results(
        cls,
        query: str,
        direction: LookupDirection,
        entries: list[DictionaryEntry],
    ):
        """Log formatted search results.

        Arguments:
            query: lookup query
            direction: lookup direction
            entries: lookup results
        """
        logger.info(
            f"Found {len(entries)} CUHK match(es) for {query!r} using {direction.value}"
        )
        for index, entry in enumerate(entries, start=1):
            logger.info(
                f"{index}. {entry.traditional} | {entry.simplified} | "
                f"Jyutping: {entry.jyutping} | Pinyin: {entry.pinyin}"
            )
            for definition in entry.definitions:
                label_prefix = f"[{definition.label}] " if definition.label else ""
                logger.info(f"   - {label_prefix}{definition.text}")


if __name__ == "__main__":
    CmnYueDictionarySearchCli.main()
