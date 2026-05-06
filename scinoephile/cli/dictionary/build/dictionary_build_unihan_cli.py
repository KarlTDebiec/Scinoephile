#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for building the Unihan dictionary cache."""

from __future__ import annotations

import zipfile
from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from typing import ClassVar

import requests

from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.dictionaries.unihan import UnihanDictionaryService
from scinoephile.dictionaries.unihan.constants import UNIHAN_SOURCE

from .dictionary_build_cli_base import DictionaryBuildCliBase

__all__ = ["DictionaryBuildUnihanCli"]

logger = getLogger(__name__)


class DictionaryBuildUnihanCli(DictionaryBuildCliBase):
    """Build Unihan dictionary cache."""

    source = UNIHAN_SOURCE
    """Dictionary source built by this CLI."""

    localizations: ClassVar[dict[str, dict[str, str]]] = {
        "zh-hans": {
            "build Unihan dictionary cache": "构建 Unihan 词典缓存",
            (
                "Data derived from Unicode Unihan files for variants, readings, and "
                "dictionary-like metadata."
            ): "由 Unicode Unihan 文件中的异体字、读音和类词典元数据整理而成的数据。",
            "download fresh Unihan.zip before building": (
                "在构建前下载最新 Unihan.zip"
            ),
            "path to Unihan_DictionaryLikeData.txt": (
                "Unihan_DictionaryLikeData.txt 的路径"
            ),
            "path to Unihan_Readings.txt": "Unihan_Readings.txt 的路径",
            "path to Unihan_Variants.txt": "Unihan_Variants.txt 的路径",
            "update source files under scinoephile/data/dictionaries/unihan": (
                "更新 scinoephile/data/dictionaries/unihan 下的源文件"
            ),
        },
        "zh-hant": {
            "build Unihan dictionary cache": "建立 Unihan 詞典快取",
            (
                "Data derived from Unicode Unihan files for variants, readings, and "
                "dictionary-like metadata."
            ): "由 Unicode Unihan 檔案中的異體字、讀音和類詞典後設資料整理而成的資料。",
            "download fresh Unihan.zip before building": (
                "在建立前下載最新 Unihan.zip"
            ),
            "path to Unihan_DictionaryLikeData.txt": (
                "Unihan_DictionaryLikeData.txt 的路徑"
            ),
            "path to Unihan_Readings.txt": "Unihan_Readings.txt 的路徑",
            "path to Unihan_Variants.txt": "Unihan_Variants.txt 的路徑",
            "update source files under scinoephile/data/dictionaries/unihan": (
                "更新 scinoephile/data/dictionaries/unihan 下的來源檔案"
            ),
        },
    }
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
            "input arguments",
            "operation arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--source-dictionary-like-data-path",
            default=None,
            type=input_file_arg(),
            help="path to Unihan_DictionaryLikeData.txt",
        )
        arg_groups["input arguments"].add_argument(
            "--source-readings-path",
            default=None,
            type=input_file_arg(),
            help="path to Unihan_Readings.txt",
        )
        arg_groups["input arguments"].add_argument(
            "--source-variants-path",
            default=None,
            type=input_file_arg(),
            help="path to Unihan_Variants.txt",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--force-download",
            action="store_true",
            help="download fresh Unihan.zip before building",
        )
        arg_groups["operation arguments"].add_argument(
            "--update-local-data",
            action="store_true",
            help="update source files under scinoephile/data/dictionaries/unihan",
        )
        cls.add_common_output_arguments(parser)

    @classmethod
    def _main(
        cls,
        *,
        database_path: Path | None,
        overwrite: bool,
        force_download: bool,
        update_local_data: bool,
        source_dictionary_like_data_path: Path | None,
        source_readings_path: Path | None,
        source_variants_path: Path | None,
    ):
        """Execute with provided keyword arguments."""
        service = UnihanDictionaryService(database_path=database_path)
        cls.log_config(
            cache_dir_path=service.runtime_data_dir_path,
            database_path=service.database_path,
            max_words=None,
            overwrite=overwrite,
            source_json_path=None,
        )
        if force_download:
            logger.info("Force download enabled")
        if update_local_data:
            logger.info("Update local data enabled")
        try:
            database_path = service.build(
                overwrite=overwrite,
                force_download=force_download,
                update_local_data=update_local_data,
                source_dictionary_like_data_path=source_dictionary_like_data_path,
                source_readings_path=source_readings_path,
                source_variants_path=source_variants_path,
            )
        except (
            FileNotFoundError,
            requests.RequestException,
            zipfile.BadZipFile,
        ) as exc:
            logger.error(str(exc))
            raise SystemExit(1) from exc
        logger.info(f"{cls.name().upper()} dictionary build complete: {database_path}")
