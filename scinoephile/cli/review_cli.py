#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle review.

Review subtitles using an LLM.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

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
from scinoephile.workflows.review import review_series, review_series_guided

from .helpers.blocks import (
    BLOCK_LOCALIZATIONS,
    add_block_range_args,
    get_block_range_indexes,
)
from .helpers.io import read_series, write_series
from .helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
    add_llm_test_case_json_arg,
    read_llm_additional_context,
)

__all__ = ["ReviewCli"]

REVIEW_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for subtitle review": "字幕审校命令行界面",
        'subtitle infile or "-" for stdin': '字幕输入文件，或使用 "-" 表示标准输入',
        "guide subtitle infile for guided review": "用于引导校对的字幕输入文件",
        "subtitle language tag (detected from infile if omitted)": (
            "字幕语言标签（省略时从输入文件检测）"
        ),
        "guide language tag (detected from guide infile if omitted)": (
            "引导字幕语言标签（省略时从引导输入文件检测）"
        ),
        "subtitle outfile path (default: stdout)": (
            "字幕输出文件路径（默认：标准输出）"
        ),
        "review subtitles using an LLM": "使用大语言模型审校字幕",
        "Review subtitles using an LLM.": "使用大语言模型审校字幕。",
    },
    "zh-hant": {
        "command-line interface for subtitle review": "字幕審校命令列介面",
        'subtitle infile or "-" for stdin': '字幕輸入檔，或使用 "-" 代表標準輸入',
        "guide subtitle infile for guided review": "用於引導校對的字幕輸入檔",
        "subtitle language tag (detected from infile if omitted)": (
            "字幕語言標籤（省略時從輸入檔偵測）"
        ),
        "guide language tag (detected from guide infile if omitted)": (
            "引導字幕語言標籤（省略時從引導輸入檔偵測）"
        ),
        "subtitle outfile path (default: stdout)": ("字幕輸出檔路徑（預設：標準輸出）"),
        "review subtitles using an LLM": "使用大型語言模型審校字幕",
        "Review subtitles using an LLM.": "使用大型語言模型審校字幕。",
    },
}
"""Localized help text keyed by locale and English source text."""


class ReviewCli(ScinoephileCliBase):
    """Review subtitles using an LLM."""

    localizations = merge_localizations(
        BLOCK_LOCALIZATIONS,
        LLM_LOCALIZATIONS,
        REVIEW_LOCALIZATIONS,
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
            "output arguments",
            "additional help",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "infile_path",
            metavar="INFILE",
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--guide-infile",
            dest="guide_infile_path",
            type=input_file_arg(),
            help="guide subtitle infile for guided review",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--language",
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="subtitle language tag (detected from infile if omitted)",
        )
        arg_groups["operation arguments"].add_argument(
            "--guide-language",
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="guide language tag (detected from guide infile if omitted)",
        )
        add_block_range_args(arg_groups["operation arguments"])
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )
        add_llm_test_case_json_arg(arg_groups["llm arguments"])

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
        guide_infile_path: Path | None,
        language: Language | None,
        guide_language: Language | None,
        first_block: int | None,
        last_block: int | None,
        llm_args: LlmArguments,
        json_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")
        if guide_language is not None and guide_infile_path is None:
            parser.error("--guide-language requires --guide-infile")

        # Read input
        target = read_series(parser, infile_path, allow_stdin=True)
        guide = None
        if guide_infile_path is not None:
            guide = read_series(parser, guide_infile_path)
            block_count = len(get_block_pair_indexes_by_pause(target, guide))
        else:
            block_count = len(target.blocks)
        start_at_idx, stop_at_idx = get_block_range_indexes(
            parser,
            first_block,
            last_block,
            block_count,
        )
        provider = get_provider(llm_args.provider_name, model=llm_args.model_name)
        additional_context = read_llm_additional_context(
            parser, llm_args.additional_context_file_path
        )

        # Perform operation
        try:
            if guide is not None:
                output = review_series_guided(
                    target,
                    guide,
                    language=language,
                    guide_language=guide_language,
                    provider=provider,
                    additional_context=additional_context,
                    test_case_path=json_path,
                    start_at_idx=start_at_idx,
                    stop_at_idx=stop_at_idx,
                )
            else:
                output = review_series(
                    target,
                    language=language,
                    provider=provider,
                    additional_context=additional_context,
                    test_case_path=json_path,
                    start_at_idx=start_at_idx,
                    stop_at_idx=stop_at_idx,
                )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        write_series(
            parser, output, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    ReviewCli.main()
