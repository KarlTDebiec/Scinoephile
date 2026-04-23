#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for building the Wiktionary dictionary cache."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from typing import Unpack

import requests

from scinoephile.common import CLIKwargs
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.dictionaries.wiktionary import WiktionaryDictionaryService

from .dictionary_build_cli_base import DictionaryBuildCliBase

__all__ = ["DictionaryBuildWiktionaryCli"]

logger = getLogger(__name__)


class DictionaryBuildWiktionaryCli(DictionaryBuildCliBase):
    """Build Wiktionary dictionary cache."""

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

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--source-jsonl-path",
            default=None,
            type=input_file_arg(),
            help="path to Kaikki Chinese Wiktionary JSONL dump",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--force-download",
            action="store_true",
            help="download fresh Kaikki JSONL before building",
        )
        arg_groups["operation arguments"].add_argument(
            "--update-local-data",
            action="store_true",
            help="update source file under scinoephile/data/dictionaries/wiktionary",
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
        force_download = kwargs.pop("force_download")
        source_jsonl_path = kwargs.pop("source_jsonl_path")
        update_local_data = kwargs.pop("update_local_data")

        service = WiktionaryDictionaryService(database_path=database_path)
        cls.log_config(
            cache_dir_path=service.runtime_data_dir_path,
            database_path=service.database_path,
            max_words=None,
            overwrite=overwrite,
            source_json_path=source_jsonl_path,
        )
        if force_download:
            logger.info("Force download enabled")
        if update_local_data:
            logger.info("Update local data enabled")
        try:
            database_path = service.build(
                overwrite=overwrite,
                force_download=force_download,
                source_jsonl_path=source_jsonl_path,
                update_local_data=update_local_data,
            )
        except (FileNotFoundError, requests.RequestException) as exc:
            logger.error(str(exc))
            raise SystemExit(1) from exc
        logger.info(f"{cls.name().upper()} dictionary build complete: {database_path}")
