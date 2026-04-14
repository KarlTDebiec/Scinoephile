#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for searching dictionaries."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
)
from scinoephile.multilang.dictionaries import DictionaryEntry
from scinoephile.multilang.dictionaries.cuhk import CuhkDictionaryService
from scinoephile.multilang.dictionaries.gzzj import GzzjDictionaryService

logger = getLogger(__name__)


class DictionarySearchCli(CommandLineInterface):
    """Command-line interface for searching dictionaries."""

    _supported_dictionaries = {
        "cuhk": CuhkDictionaryService,
        "gzzj": GzzjDictionaryService,
    }

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
            type=input_file_arg(),
            help="SQLite database input path",
        )
        arg_groups["input arguments"].add_argument(
            "--dictionary-name",
            default="all",
            choices=["all", *sorted(cls._supported_dictionaries)],
            help="dictionary to search, or all available dictionaries",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "query",
            type=str,
            help="Mandarin or Cantonese query text",
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
        database_path = kwargs.pop("database_path")
        dictionary_name = kwargs.pop("dictionary_name")
        query = kwargs.pop("query")
        limit = kwargs.pop("limit")

        try:
            entries = cls._search_dictionaries(
                query=query,
                limit=limit,
                dictionary_name=dictionary_name,
                database_path=database_path,
            )
        except ValueError as exc:
            logger.error(f"Unsupported query {query!r}: {exc}")
            raise SystemExit(1) from exc
        except FileNotFoundError as exc:
            logger.error(str(exc))
            raise SystemExit(1) from exc
        cls._log_search_results(query, entries, dictionary_name)

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
        entries: list[DictionaryEntry],
        dictionary_name: str,
    ):
        """Log formatted search results.

        Arguments:
            query: lookup query
            entries: lookup results
            dictionary_name: requested dictionary selector
        """
        logger.info(
            f"Found {len(entries)} match(es) in {dictionary_name} for {query!r}"
        )
        for index, entry in enumerate(entries, start=1):
            logger.info(
                f"{index}. {entry.traditional} | {entry.simplified} | "
                f"Jyutping: {entry.jyutping} | Pinyin: {entry.pinyin}"
            )
            for definition in entry.definitions:
                label_prefix = f"[{definition.label}] " if definition.label else ""
                logger.info(f"   - {label_prefix}{definition.text}")

    @classmethod
    def _search_dictionaries(
        cls,
        *,
        query: str,
        limit: int,
        dictionary_name: str,
        database_path: Path | None,
    ) -> list[DictionaryEntry]:
        """Search one or more configured dictionaries.

        Arguments:
            query: lookup query
            limit: max results per dictionary
            dictionary_name: dictionary selector
            database_path: optional explicit database path for single-dictionary search
        Returns:
            deduplicated dictionary entries
        """
        names = (
            sorted(cls._supported_dictionaries)
            if dictionary_name == "all"
            else [dictionary_name]
        )
        if dictionary_name == "all" and database_path is not None:
            raise FileNotFoundError(
                "--database-path may only be used with a specific --dictionary-name"
            )

        entries: list[DictionaryEntry] = []
        missing_dictionaries: list[str] = []
        available_dictionary_count = 0
        for name in names:
            service = cls._supported_dictionaries[name](
                database_path=database_path,
                auto_build_missing=False,
            )
            try:
                entries.extend(service.lookup(query=query, limit=limit))
                available_dictionary_count += 1
            except FileNotFoundError:
                missing_dictionaries.append(name)

        if entries or available_dictionary_count > 0:
            entries_by_key = {
                (
                    entry.traditional,
                    entry.simplified,
                    entry.pinyin,
                    entry.jyutping,
                ): entry
                for entry in entries
            }
            return list(entries_by_key.values())

        if missing_dictionaries:
            if dictionary_name == "all":
                missing_display = ", ".join(sorted(missing_dictionaries))
                raise FileNotFoundError(
                    "No searchable dictionary databases were found. Build one or more "
                    f"of: {missing_display}."
                )
            raise FileNotFoundError(
                f"{dictionary_name.upper()} dictionary database not found."
            )
        return []


if __name__ == "__main__":
    DictionarySearchCli.main()
