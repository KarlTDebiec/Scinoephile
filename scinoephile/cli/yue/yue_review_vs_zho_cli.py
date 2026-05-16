#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese review against standard Chinese."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.llms import (
    LLM_LOCALIZATIONS,
    add_llm_provider_arguments,
    read_llm_additional_context,
)
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.yue_zho.block_review import (
    YueBlockReviewVsZhoPromptYueHans,
    YueBlockReviewVsZhoPromptYueHant,
    get_yue_block_reviewed_vs_zho,
    get_yue_vs_zho_block_reviewer,
)
from scinoephile.multilang.yue_zho.line_review import (
    YueLineReviewVsZhoPromptYueHans,
    YueLineReviewVsZhoPromptYueHant,
    get_yue_line_reviewed_vs_zho,
    get_yue_vs_zho_line_reviewer,
)

__all__ = ["YueReviewVsZhoCli"]

YUE_REVIEW_VS_ZHO_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        (
            "command-line interface for written Cantonese review against "
            "standard Chinese"
        ): "书面粤语对照标准中文校对命令行界面",
        (
            "review mode (default: block): block=block-by-block review, "
            "line=line-by-line review"
        ): "校对模式（默认：block）：block=按区块校对，line=按行校对",
        "reviewed written Cantonese subtitle outfile path (default: stdout)": (
            "校对后的书面粤语字幕输出文件路径（默认：标准输出）"
        ),
        (
            "review written Cantonese subtitles against standard Chinese subtitles"
        ): "校对书面粤语字幕与标准中文字幕",
        "script for prompts and output conversion (default: simplified)": (
            "提示词和输出转换使用的字形（默认：简体）"
        ),
        'target written Cantonese subtitle infile path or "-" for stdin': (
            '目标书面粤语字幕输入文件路径，或使用 "-" 表示标准输入'
        ),
        'reference standard Chinese subtitle infile path or "-" for stdin': (
            '参考标准中文字幕输入文件路径，或使用 "-" 表示标准输入'
        ),
    },
    "zh-hant": {
        (
            "command-line interface for written Cantonese review against "
            "standard Chinese"
        ): "書面粵語對照標準中文校對命令列介面",
        (
            "review mode (default: block): block=block-by-block review, "
            "line=line-by-line review"
        ): "校對模式（預設：block）：block=按區塊校對，line=按行校對",
        "reviewed written Cantonese subtitle outfile path (default: stdout)": (
            "校對後的書面粵語字幕輸出檔路徑（預設：標準輸出）"
        ),
        (
            "review written Cantonese subtitles against standard Chinese subtitles"
        ): "校對書面粵語字幕與標準中文字幕",
        "script for prompts and output conversion (default: simplified)": (
            "提示詞與輸出轉換使用的字形（預設：簡體）"
        ),
        'target written Cantonese subtitle infile path or "-" for stdin': (
            '目標書面粵語字幕輸入檔路徑，或使用 "-" 代表標準輸入'
        ),
        'reference standard Chinese subtitle infile path or "-" for stdin': (
            '參考標準中文字幕輸入檔路徑，或使用 "-" 代表標準輸入'
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class YueReviewVsZhoCli(ScinoephileCliBase):
    """Review written Cantonese subtitles against standard Chinese subtitles."""

    localizations = merge_localizations(
        LLM_LOCALIZATIONS,
        YUE_REVIEW_VS_ZHO_LOCALIZATIONS,
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
            "output arguments",
            "additional help",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--yue-infile",
            dest="yue_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='target written Cantonese subtitle infile path or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--zho-infile",
            dest="zho_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='reference standard Chinese subtitle infile path or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--mode",
            default="block",
            choices=("block", "line"),
            type=str_arg(options=("block", "line")),
            help=(
                "review mode (default: block): "
                "block=block-by-block review, line=line-by-line review"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--script",
            default="simplified",
            choices=("simplified", "traditional"),
            type=str_arg(options=("simplified", "traditional")),
            help="script for prompts and output conversion (default: simplified)",
        )
        add_llm_provider_arguments(
            arg_groups["operation arguments"], arg_groups["additional help"]
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            dest="outfile_path",
            type=output_file_arg(),
            help="reviewed written Cantonese subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "review-vs-zho"

    @classmethod
    def _get_line_review_prompt_cls(
        cls, script: str
    ) -> type[YueLineReviewVsZhoPromptYueHans]:
        """Get the line-review prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            line-review prompt class
        """
        if script == "traditional":
            return YueLineReviewVsZhoPromptYueHant
        return YueLineReviewVsZhoPromptYueHans

    @classmethod
    def _get_block_review_prompt_cls(
        cls, script: str
    ) -> type[YueBlockReviewVsZhoPromptYueHans]:
        """Get the block review prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            block review prompt class
        """
        if script == "traditional":
            return YueBlockReviewVsZhoPromptYueHant
        return YueBlockReviewVsZhoPromptYueHans

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        yue_infile_path: Path | str,
        zho_infile_path: Path | str,
        mode: str,
        script: str,
        llm_provider_name: str,
        llm_model_name: str | None,
        llm_additional_context_file_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if yue_infile_path == "-" and zho_infile_path == "-":
            parser.error("--yue-infile and --zho-infile may not both be '-'")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        # Read inputs
        yuewen = read_series(parser, yue_infile_path, allow_stdin=True)
        zhongwen = read_series(parser, zho_infile_path, allow_stdin=True)
        additional_context = read_llm_additional_context(
            parser, llm_additional_context_file_path
        )
        provider = get_provider(llm_provider_name, model=llm_model_name)

        # Perform operations
        if mode == "line":
            prompt_cls = cls._get_line_review_prompt_cls(script)
            line_reviewer = get_yue_vs_zho_line_reviewer(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            reviewed = get_yue_line_reviewed_vs_zho(
                yuewen=yuewen,
                zhongwen=zhongwen,
                line_reviewer=line_reviewer,
            )
        else:
            prompt_cls = cls._get_block_review_prompt_cls(script)
            reviewer = get_yue_vs_zho_block_reviewer(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            reviewed = get_yue_block_reviewed_vs_zho(
                yuewen=yuewen,
                zhongwen=zhongwen,
                reviewer=reviewer,
            )

        # Write outputs
        write_series(
            parser,
            reviewed,
            outfile_path if outfile_path is not None else "-",
            overwrite,
        )


if __name__ == "__main__":
    YueReviewVsZhoCli.main()
