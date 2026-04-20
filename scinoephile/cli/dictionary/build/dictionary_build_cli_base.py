#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base class for dictionary build CLIs."""

from __future__ import annotations

import re
from abc import ABC
from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

from scinoephile.common import CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, output_file_arg

__all__ = ["DictionaryBuildCliBase"]

logger = getLogger(__name__)


class DictionaryBuildCliBase(CommandLineInterface, ABC):
    """Base class for building a specific dictionary cache."""

    @classmethod
    def add_common_output_arguments(cls, parser: ArgumentParser):
        """Add output arguments shared by dictionary build subcommands.

        Arguments:
            parser: nascent argument parser
        """
        arg_groups = get_arg_groups_by_name(
            parser,
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "--database-path",
            default=None,
            type=output_file_arg(exist_ok=True),
            help="SQLite database output path",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite the existing SQLite database if it already exists",
        )

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
        """Log the effective build configuration.

        Arguments:
            cache_dir_path: cache directory path
            database_path: SQLite database path
            max_words: optional max words cap
            overwrite: whether database overwrite is enabled
            source_json_path: optional manually downloaded source JSON
        """
        logger.info(f"Building dictionary: {cls.name()}")
        if cache_dir_path is not None:
            logger.info(f"Using cache directory: {cache_dir_path}")
        if source_json_path is not None:
            logger.info(f"Using source JSON: {source_json_path}")
        logger.info(f"Using SQLite database: {database_path}")
        if max_words is not None:
            logger.info(f"Building at most {max_words} discovered words")
        if overwrite:
            logger.info("Overwrite enabled")

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return re.sub(r"^DictionaryBuild|Cli$", "", cls.__name__).lower()
