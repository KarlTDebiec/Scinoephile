#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for building the GZZJ dictionary cache."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.cli.dictionary_build_cli_base import DictionaryBuildCliBase
from scinoephile.common import CLIKwargs
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.multilang.dictionaries.gzzj import GzzjDictionaryService

__all__ = [
    "DictionaryBuildGzzjCli",
]


class DictionaryBuildGzzjCli(DictionaryBuildCliBase):
    """Command-line interface for building the GZZJ dictionary cache."""

    dictionary_name = "gzzj"

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
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        arg_groups["input arguments"].add_argument(
            "--source-json-path",
            metavar="FILE",
            default=None,
            type=input_file_arg(),
            help="path to manually downloaded GZZJ source JSON",
        )
        cls.add_common_output_arguments(parser)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        database_path = kwargs.pop("database_path")
        overwrite = kwargs.pop("overwrite")
        source_json_path = kwargs.pop("source_json_path")

        service = GzzjDictionaryService(
            database_path=database_path,
            source_json_path=source_json_path,
        )
        cls.log_config(
            cache_dir_path=None,
            database_path=service.database_path,
            max_words=None,
            overwrite=overwrite,
            source_json_path=source_json_path,
        )
        try:
            database_path = service.build(overwrite=overwrite)
        except FileNotFoundError as exc:
            cls.log_file_not_found_and_exit(exc)
        cls.log_completion(database_path)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "gzzj"
