#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for building the CUHK dictionary cache."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from typing import ClassVar

from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    int_arg,
    output_dir_arg,
)
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.dictionaries.cuhk import CuhkDictionaryService
from scinoephile.dictionaries.cuhk.constants import CUHK_SOURCE

from .dictionary_build_cli_base import DictionaryBuildCliBase

__all__ = ["DictionaryBuildCuhkCli"]

logger = getLogger(__name__)


class DictionaryBuildCuhkCli(DictionaryBuildCliBase):
    """Build CUHK dictionary cache."""

    source = CUHK_SOURCE
    """Dictionary source built by this CLI."""

    localizations: ClassVar[dict[str, dict[str, str]]] = {
        "zh-hans": {
            "build CUHK dictionary cache": "构建 CUHK 词典缓存",
            ("cache directory for scraped HTML and link data (default: %(default)s)"): (
                "抓取 HTML 与链接数据的缓存目录（默认：%(default)s）"
            ),
            (
                "Comparative Database of Modern Standard Chinese and Cantonese "
                "(Chinese University of Hong Kong)."
            ): "香港中文大学现代标准汉语与粤语对照数据库。",
            "maximum delay between HTTP requests": "HTTP 请求之间的最大延迟",
            "maximum retries per HTTP request": "每个 HTTP 请求的最大重试次数",
            "minimum delay between HTTP requests": "HTTP 请求之间的最小延迟",
            "per-request timeout in seconds": "每次请求的超时时间（秒）",
            "stop after building the first N discovered words": (
                "在构建前 N 个已发现词条后停止"
            ),
        },
        "zh-hant": {
            "build CUHK dictionary cache": "建立 CUHK 詞典快取",
            ("cache directory for scraped HTML and link data (default: %(default)s)"): (
                "擷取 HTML 與連結資料的快取目錄（預設：%(default)s）"
            ),
            (
                "Comparative Database of Modern Standard Chinese and Cantonese "
                "(Chinese University of Hong Kong)."
            ): "香港中文大學現代標準漢語與粵語對照資料庫。",
            "maximum delay between HTTP requests": "HTTP 請求之間的最大延遲",
            "maximum retries per HTTP request": "每個 HTTP 請求的最大重試次數",
            "minimum delay between HTTP requests": "HTTP 請求之間的最小延遲",
            "per-request timeout in seconds": "每次請求的逾時時間（秒）",
            "stop after building the first N discovered words": (
                "在建立前 N 個已發現詞條後停止"
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
            "--cache-dir",
            dest="cache_dir_path",
            default=get_runtime_cache_dir_path("dictionaries", "cuhk"),
            type=output_dir_arg(),
            help=(
                "cache directory for scraped HTML and link data (default: %(default)s)"
            ),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--max-words",
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
    def _main(
        cls,
        *,
        cache_dir_path: Path | None,
        database_path: Path | None,
        max_words: int | None,
        overwrite: bool,
        min_delay_seconds: float,
        max_delay_seconds: float,
        max_retries: int,
        request_timeout_seconds: float,
    ):
        """Execute with provided keyword arguments."""
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
            logger.error(str(exc))
            raise SystemExit(1) from exc
        logger.info(f"{cls.name().upper()} dictionary build complete: {database_path}")
