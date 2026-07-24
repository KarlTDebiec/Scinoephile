#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle translation.

Translate subtitles between supported languages.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.core.pairs import get_block_pair_indexes_by_pause
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.translation import (
    translate_series,
    translate_series_gaps,
    translate_series_guided,
)

from .helpers.blocks import (
    BLOCK_LOCALIZATIONS,
    add_block_range_args,
    get_block_range_indexes,
)
from .helpers.cache import CACHE_LOCALIZATIONS, CacheArguments, add_cache_args
from .helpers.io import read_series, write_series
from .helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
    add_llm_test_case_json_arg,
    read_llm_additional_context,
)

__all__ = ["TranslateCli"]

TRANSLATE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for subtitle translation": "字幕翻译命令行界面",
        "Translate subtitles between supported languages.": (
            "在受支持的语言之间翻译字幕。"
        ),
        'source subtitle infile or "-" for stdin': (
            '源字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "target-language subtitle infile with gaps to fill": (
            "含缺口、需补全的目标语言字幕输入文件"
        ),
        "target-language subtitle infile with which to guide translation": (
            "用于指导翻译的目标语言字幕输入文件"
        ),
        "source language (detected from infile if omitted)": (
            "源语言（省略时从输入文件检测）"
        ),
        "target language (required unless guide or gapped input is detected)": (
            "目标语言（除非可从引导或缺口输入检测，否则必填）"
        ),
        "subtitle outfile path (default: stdout)": (
            "字幕输出文件路径（默认：标准输出）"
        ),
        "translate subtitles between supported languages": (
            "在受支持的语言之间翻译字幕"
        ),
    },
    "zh-hant": {
        "command-line interface for subtitle translation": "字幕翻譯命令列介面",
        "Translate subtitles between supported languages.": (
            "在支援的語言之間翻譯字幕。"
        ),
        'source subtitle infile or "-" for stdin': (
            '來源字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "target-language subtitle infile with gaps to fill": (
            "含缺口、需補全的目標語言字幕輸入檔"
        ),
        "target-language subtitle infile with which to guide translation": (
            "用於指導翻譯的目標語言字幕輸入檔"
        ),
        "source language (detected from infile if omitted)": (
            "來源語言（省略時從輸入檔偵測）"
        ),
        "target language (required unless guide or gapped input is detected)": (
            "目標語言（除非可從引導或缺口輸入偵測，否則必填）"
        ),
        "subtitle outfile path (default: stdout)": ("字幕輸出檔路徑（預設：標準輸出）"),
        "translate subtitles between supported languages": ("在支援的語言之間翻譯字幕"),
    },
}
"""Localized help text keyed by locale and English source text."""


class TranslateCli(ScinoephileCliBase):
    """Translate subtitles between supported languages."""

    localizations = merge_localizations(
        BLOCK_LOCALIZATIONS,
        CACHE_LOCALIZATIONS,
        LLM_LOCALIZATIONS,
        TRANSLATE_LOCALIZATIONS,
    )
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
            "llm arguments",
            "cache arguments",
            "output arguments",
            "additional help",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "infile_path",
            metavar="INFILE",
            type=input_file_arg(allow_stdin=True),
            help='source subtitle infile or "-" for stdin',
        )
        target_input_group = arg_groups[
            "input arguments"
        ].add_mutually_exclusive_group()
        target_input_group.add_argument(
            "--gapped-infile",
            dest="gapped_infile_path",
            type=input_file_arg(),
            help="target-language subtitle infile with gaps to fill",
        )
        target_input_group.add_argument(
            "--guide-infile",
            dest="guide_infile_path",
            type=input_file_arg(),
            help="target-language subtitle infile with which to guide translation",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--source-language",
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="source language (detected from infile if omitted)",
        )
        arg_groups["operation arguments"].add_argument(
            "--target-language",
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help=(
                "target language (required unless guide or gapped input is detected)"
            ),
        )
        add_block_range_args(arg_groups["operation arguments"])
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )
        add_llm_test_case_json_arg(arg_groups["llm arguments"])

        # Cache arguments
        add_cache_args(arg_groups["cache arguments"])

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
            help="subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path | str,
        gapped_infile_path: Path | str | None,
        guide_infile_path: Path | str | None,
        source_language: Language | None,
        target_language: Language | None,
        first_block: int | None,
        last_block: int | None,
        llm_args: LlmArguments,
        cache_args: CacheArguments,
        json_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        # Read inputs
        source = read_series(parser, infile_path, allow_stdin=True)
        target = None
        guide = None
        if gapped_infile_path is not None:
            target = read_series(parser, gapped_infile_path)
            block_count = len(get_block_pair_indexes_by_pause(source, target))
        elif guide_infile_path is not None:
            guide = read_series(parser, guide_infile_path)
            block_count = len(get_block_pair_indexes_by_pause(source, guide))
        else:
            block_count = len(source.blocks)
        start_at_idx, stop_at_idx = get_block_range_indexes(
            parser,
            first_block,
            last_block,
            block_count,
        )
        kwargs: dict[str, Any] = {
            "source_language": source_language,
            "target_language": target_language,
            "provider": get_provider(llm_args.provider_name, model=llm_args.model_name),
            "additional_context": read_llm_additional_context(
                parser, llm_args.additional_context_file_path
            ),
            "cache_dir_path": cache_args.dir_path / "llm",
            "overwrite_cache": cache_args.overwrite,
            "test_case_path": json_path,
            "start_at_idx": start_at_idx,
            "stop_at_idx": stop_at_idx,
        }

        # Perform operation
        try:
            if target is not None:
                output = translate_series_gaps(source, target, **kwargs)
            elif guide is not None:
                output = translate_series_guided(source, guide, **kwargs)
            else:
                if target_language is None:
                    parser.error("--target-language is required")
                kwargs["target_language"] = target_language
                output = translate_series(source, **kwargs)
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        write_series(
            parser, output, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    TranslateCli.main()
