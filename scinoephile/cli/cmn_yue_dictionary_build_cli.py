#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for building the CUHK dictionary cache."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    int_arg,
    output_dir_arg,
)
from scinoephile.multilang.cmn_yue.dictionaries.cuhk import CuhkDictionaryBuilder

logger = getLogger(__name__)


class CmnYueDictionaryBuildCli(CommandLineInterface):
    """Command-line interface for building the CUHK dictionary cache."""

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

        arg_groups["input arguments"].add_argument(
            "--cache-dir",
            metavar="DIR",
            default=None,
            type=output_dir_arg(),
            help="cache directory for scraped HTML and link data",
        )
        arg_groups["operation arguments"].add_argument(
            "--max-words",
            metavar="N",
            type=int_arg(min_value=1),
            help="stop after building the first N discovered words",
        )
        arg_groups["operation arguments"].add_argument(
            "--force-rebuild",
            action="store_true",
            help="rebuild even if a local CUHK database already exists",
        )
        arg_groups["operation arguments"].add_argument(
            "--min-delay-seconds",
            type=float_arg(min_value=0.0),
            default=5.0,
            help="minimum delay between HTTP requests",
        )
        arg_groups["operation arguments"].add_argument(
            "--max-delay-seconds",
            type=float_arg(min_value=0.0),
            default=10.0,
            help="maximum delay between HTTP requests",
        )
        arg_groups["operation arguments"].add_argument(
            "--max-retries",
            type=int_arg(min_value=1),
            default=5,
            help="maximum retries per HTTP request",
        )
        arg_groups["operation arguments"].add_argument(
            "--request-timeout-seconds",
            type=float_arg(min_value=0.1),
            default=30.0,
            help="per-request timeout in seconds",
        )
        parser.set_defaults(verbosity=2)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        cache_dir_path = kwargs.pop("cache_dir")
        max_words = kwargs.pop("max_words", None)
        force_rebuild = kwargs.pop("force_rebuild")
        min_delay_seconds = kwargs.pop("min_delay_seconds")
        max_delay_seconds = kwargs.pop("max_delay_seconds")
        max_retries = kwargs.pop("max_retries")
        request_timeout_seconds = kwargs.pop("request_timeout_seconds")

        builder = CuhkDictionaryBuilder(
            cache_dir_path=cache_dir_path,
            min_delay_seconds=min_delay_seconds,
            max_delay_seconds=max_delay_seconds,
            max_retries=max_retries,
            request_timeout_seconds=request_timeout_seconds,
        )
        cls._log_build_configuration(
            builder.cache_dir_path,
            builder.database_path,
            max_words,
            force_rebuild,
        )
        database_path = builder.build(
            force_rebuild=force_rebuild,
            max_words=max_words,
        )
        logger.info(f"CUHK dictionary build complete: {database_path}")

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "build"

    @classmethod
    def _log_build_configuration(
        cls,
        cache_dir_path: Path,
        database_path: Path,
        max_words: int | None,
        force_rebuild: bool,
    ):
        """Log the effective build configuration.

        Arguments:
            cache_dir_path: cache directory path
            database_path: SQLite database path
            max_words: optional max words cap
            force_rebuild: whether rebuild is forced
        """
        logger.info(f"Using CUHK scrape cache directory: {cache_dir_path}")
        logger.info(f"Writing CUHK SQLite database to: {database_path}")
        if max_words is None:
            logger.info("Building all discovered CUHK words")
        else:
            logger.info(f"Building at most {max_words} discovered CUHK words")
        if force_rebuild:
            logger.info("Force rebuild enabled")


if __name__ == "__main__":
    CmnYueDictionaryBuildCli.main()
