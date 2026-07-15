#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle proofreading.

Proofread subtitles using an LLM.
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
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.review import (
    review_series,
    review_series_guided,
    review_series_pairwise,
)

from .helpers.io import read_series, write_series
from .helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
    read_llm_additional_context,
)

__all__ = ["ProofreadCli"]

PROOFREAD_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for subtitle proofreading": "字幕校对命令行界面",
        'subtitle infile or "-" for stdin': '字幕输入文件，或使用 "-" 表示标准输入',
        "pairwise guide subtitle infile": "用于逐对校对的引导字幕输入文件",
        "guide subtitle infile for guided review": "用于引导校对的字幕输入文件",
        "subtitle language tag (detected from infile if omitted)": (
            "字幕语言标签（省略时从输入文件检测）"
        ),
        "reference or guide language tag (detected from its infile if omitted)": (
            "参考或引导字幕语言标签（省略时从相应输入文件检测）"
        ),
        "subtitle outfile path (default: stdout)": (
            "字幕输出文件路径（默认：标准输出）"
        ),
        "proofread subtitles using an LLM": "使用大语言模型校对字幕",
        "Proofread subtitles using an LLM.": "使用大语言模型校对字幕。",
    },
    "zh-hant": {
        "command-line interface for subtitle proofreading": "字幕校對命令列介面",
        'subtitle infile or "-" for stdin': '字幕輸入檔，或使用 "-" 代表標準輸入',
        "pairwise guide subtitle infile": "用於逐對校對的引導字幕輸入檔",
        "guide subtitle infile for guided review": "用於引導校對的字幕輸入檔",
        "subtitle language tag (detected from infile if omitted)": (
            "字幕語言標籤（省略時從輸入檔偵測）"
        ),
        "reference or guide language tag (detected from its infile if omitted)": (
            "參考或引導字幕語言標籤（省略時從相應輸入檔偵測）"
        ),
        "subtitle outfile path (default: stdout)": ("字幕輸出檔路徑（預設：標準輸出）"),
        "proofread subtitles using an LLM": "使用大型語言模型校對字幕",
        "Proofread subtitles using an LLM.": "使用大型語言模型校對字幕。",
    },
}
"""Localized help text keyed by locale and English source text."""


class ProofreadCli(ScinoephileCliBase):
    """Proofread subtitles using an LLM."""

    localizations = merge_localizations(
        LLM_LOCALIZATIONS,
        PROOFREAD_LOCALIZATIONS,
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
        guide_input_group = arg_groups["input arguments"].add_mutually_exclusive_group()
        guide_input_group.add_argument(
            "--pairwise-guide-infile",
            dest="pairwise_guide_infile_path",
            type=input_file_arg(),
            help="pairwise guide subtitle infile",
        )
        guide_input_group.add_argument(
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
            "--reference-language",
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help=(
                "reference or guide language tag (detected from its infile if omitted)"
            ),
        )
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )

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
        pairwise_guide_infile_path: Path | None,
        guide_infile_path: Path | None,
        language: Language | None,
        reference_language: Language | None,
        llm_args: LlmArguments,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")
        if (
            reference_language is not None
            and pairwise_guide_infile_path is None
            and guide_infile_path is None
        ):
            parser.error(
                "--reference-language requires --pairwise-guide-infile or "
                "--guide-infile"
            )

        # Read input
        series = read_series(parser, infile_path, allow_stdin=True)
        provider = get_provider(llm_args.provider_name, model=llm_args.model_name)
        additional_context = read_llm_additional_context(
            parser, llm_args.additional_context_file_path
        )

        # Perform operation
        try:
            if pairwise_guide_infile_path is not None:
                reference = read_series(parser, pairwise_guide_infile_path)
                output = review_series_pairwise(
                    series,
                    reference,
                    language=language,
                    reference_language=reference_language,
                    provider=provider,
                    additional_context=additional_context,
                )
            elif guide_infile_path is not None:
                guide = read_series(parser, guide_infile_path)
                output = review_series_guided(
                    series,
                    guide,
                    language=language,
                    guide_language=reference_language,
                    provider=provider,
                    additional_context=additional_context,
                )
            else:
                output = review_series(
                    series,
                    language=language,
                    provider=provider,
                    additional_context=additional_context,
                )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        write_series(
            parser, output, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    ProofreadCli.main()
