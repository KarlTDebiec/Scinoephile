#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for searching installed 中文/粤文 dictionaries."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
)
from scinoephile.core.dictionaries import DictionaryLookupResult, LookupDirection
from scinoephile.multilang.cmn_yue.dictionaries.service import CmnYueDictionaryService

logger = getLogger(__name__)


class CmnYueDictionarySearchCli(CommandLineInterface):
    """Command-line interface for searching installed 中文/粤文 dictionaries."""

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
            "operation arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--database-path",
            metavar="FILE",
            default=None,
            action="append",
            type=input_file_arg(),
            help="SQLite database input path, may be specified more than once",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "query",
            type=str,
            help="Mandarin or Cantonese query text",
        )
        arg_groups["operation arguments"].add_argument(
            "--direction",
            type=LookupDirection,
            choices=list(LookupDirection),
            default=LookupDirection.CMN_TO_YUE,
            help="lookup direction",
        )
        arg_groups["operation arguments"].add_argument(
            "--source",
            metavar="SOURCE",
            default=None,
            action="append",
            type=str,
            help="optional source id filter, may be specified more than once",
        )
        arg_groups["operation arguments"].add_argument(
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
        database_paths = kwargs.pop("database_path")
        query = kwargs.pop("query")
        direction = kwargs.pop("direction")
        source_ids = kwargs.pop("source")
        limit = kwargs.pop("limit")

        service = CmnYueDictionaryService(
            database_paths=database_paths,
        )
        results = service.lookup(
            query=query,
            direction=direction,
            limit=limit,
            source_ids=source_ids,
        )
        cls._log_search_results(query, direction, results)

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
        results: list[DictionaryLookupResult],
    ):
        """Log formatted search results.

        Arguments:
            query: lookup query
            direction: lookup direction
            results: lookup results
        """
        logger.info(
            f"Found {len(results)} match(es) for {query!r} using {direction.value}"
        )
        for index, result in enumerate(results, start=1):
            entry = result.entry
            logger.info(
                f"{index}. [{result.source.shortname}] "
                f"{entry.traditional} | {entry.simplified} | "
                f"Jyutping: {entry.jyutping} | Pinyin: {entry.pinyin}"
            )
            for definition in entry.definitions:
                label_prefix = f"[{definition.label}] " if definition.label else ""
                logger.info(f"   - {label_prefix}{definition.text}")


if __name__ == "__main__":
    CmnYueDictionarySearchCli.main()
