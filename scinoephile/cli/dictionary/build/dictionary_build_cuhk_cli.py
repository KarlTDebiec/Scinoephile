#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for building the CUHK dictionary cache."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from typing import Unpack

from scinoephile.common import CLIKwargs
from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    int_arg,
    output_dir_arg,
)
from scinoephile.multilang.dictionaries.cuhk import CuhkDictionaryService

from .dictionary_build_cli_base import DictionaryBuildCliBase

__all__ = ["DictionaryBuildCuhkCli"]

logger = getLogger(__name__)


class DictionaryBuildCuhkCli(DictionaryBuildCliBase):
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
            "output arguments",
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
            "--min-delay-seconds",
            type=float_arg(min_value=0.0),
            default=1.0,
            help="minimum delay between HTTP requests",
        )
        arg_groups["operation arguments"].add_argument(
            "--max-delay-seconds",
            type=float_arg(min_value=0.0),
            default=5.0,
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
        cls.add_common_output_arguments(parser)

    @classmethod
    def log_config(
        cls,
        *,
        cache_dir_path: Path | None,
        database_path: Path,
        max_words: int | None,
        overwrite: bool,
        source_json_path: Path | None,
    ):
        """Log the effective CUHK build configuration.

        Arguments:
            cache_dir_path: cache directory path
            database_path: SQLite database path
            max_words: optional max words cap
            overwrite: whether database overwrite is enabled
            source_json_path: unused source JSON path
        """
        super().log_config(
            cache_dir_path=cache_dir_path,
            database_path=database_path,
            max_words=None,
            overwrite=overwrite,
            source_json_path=source_json_path,
        )
        if max_words is None:
            logger.info("Building all discovered CUHK words")
        else:
            logger.info(f"Building at most {max_words} discovered CUHK words")

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        cache_dir_path = kwargs.pop("cache_dir")
        database_path = kwargs.pop("database_path")
        max_words = kwargs.pop("max_words", None)
        overwrite = kwargs.pop("overwrite")
        min_delay_seconds = kwargs.pop("min_delay_seconds")
        max_delay_seconds = kwargs.pop("max_delay_seconds")
        max_retries = kwargs.pop("max_retries")
        request_timeout_seconds = kwargs.pop("request_timeout_seconds")

        service = CuhkDictionaryService(
            database_path=database_path,
            scraper_kwargs={
                "cache_dir_path": cache_dir_path,
                "min_delay_seconds": min_delay_seconds,
                "max_delay_seconds": max_delay_seconds,
                "max_retries": max_retries,
                "request_timeout_seconds": request_timeout_seconds,
            },
        )
        cls.log_config(
            cache_dir_path=service.cache_dir_path,
            database_path=service.database_path,
            max_words=max_words,
            overwrite=overwrite,
            source_json_path=None,
        )
        try:
            database_path = service.build(
                overwrite=overwrite,
                max_words=max_words,
            )
        except FileNotFoundError as exc:
            cls.log_file_not_found_and_exit(exc)
        cls.log_completion(database_path)
