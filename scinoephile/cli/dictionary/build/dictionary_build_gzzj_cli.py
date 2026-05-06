#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for building the GZZJ dictionary cache."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from typing import ClassVar

from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.dictionaries.gzzj import GzzjDictionaryService
from scinoephile.dictionaries.gzzj.constants import GZZJ_SOURCE

from .dictionary_build_cli_base import DictionaryBuildCliBase

__all__ = ["DictionaryBuildGzzjCli"]

logger = getLogger(__name__)


class DictionaryBuildGzzjCli(DictionaryBuildCliBase):
    """Build GZZJ dictionary cache."""

    source = GZZJ_SOURCE
    """Dictionary source built by this CLI."""

    localizations: ClassVar[dict[str, dict[str, str]]] = {
        "zh-hans": {
            "build GZZJ dictionary cache": "构建 GZZJ 词典缓存",
            (
                "Digital data derived from the 2004 second edition of "
                "《廣州話正音字典》."
            ): "由 2004 年第二版《广州话正音字典》整理而成的数字数据。",
            "path to manually downloaded GZZJ source JSON": (
                "手动下载的 GZZJ 源 JSON 路径"
            ),
        },
        "zh-hant": {
            "build GZZJ dictionary cache": "建立 GZZJ 詞典快取",
            (
                "Digital data derived from the 2004 second edition of "
                "《廣州話正音字典》."
            ): "由 2004 年第二版《廣州話正音字典》整理而成的數碼資料。",
            "path to manually downloaded GZZJ source JSON": (
                "手動下載的 GZZJ 來源 JSON 路徑"
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
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--source-json-path",
            default=None,
            type=input_file_arg(),
            help="path to manually downloaded GZZJ source JSON",
        )
        cls.add_common_output_arguments(parser)

    @classmethod
    def _main(
        cls,
        *,
        database_path: Path | None,
        overwrite: bool,
        source_json_path: Path | None,
    ):
        """Execute with provided keyword arguments."""
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
            logger.error(str(exc))
            raise SystemExit(1) from exc
        logger.info(f"{cls.name().upper()} dictionary build complete: {database_path}")
