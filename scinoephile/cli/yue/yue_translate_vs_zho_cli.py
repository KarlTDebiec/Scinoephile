#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese gap translation.

This command fills empty written Cantonese subtitle lines using the
corresponding standard Chinese subtitle lines as reference.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.llms import LLM_LOCALIZATIONS, add_llm_provider_arguments
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.yue_zho.gapped_translation import (
    YueGappedTranslationVsZhoPromptYueHans,
    YueGappedTranslationVsZhoPromptYueHant,
    get_yue_gapped_translated_vs_zho,
    get_yue_vs_zho_gapped_translator,
)

__all__ = ["YueTranslateVsZhoCli"]

YUE_TRANSLATE_VS_ZHO_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for written Cantonese gap translation": (
            "书面粤语缺口翻译命令行界面"
        ),
        "This command fills empty written Cantonese subtitle lines using the "
        "corresponding standard Chinese subtitle lines as reference.": (
            "此命令使用对应的标准中文字幕作为参考，补全空白的书面粤语字幕行。"
        ),
        'aligned standard Chinese subtitle infile or "-" for stdin': (
            '已对齐的标准中文字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "script for prompts and output conversion (default: simplified)": (
            "提示词和输出转换使用的字形（默认：简体）"
        ),
        'written Cantonese subtitle infile with gaps, or "-" for stdin': (
            '含缺口的书面粤语字幕输入文件，或使用 "-" 表示标准输入'
        ),
        (
            "gap-filled written Cantonese subtitle outfile path (default: stdout)"
        ): "补全缺口后的书面粤语字幕输出文件路径（默认：标准输出）",
        "fill missing written Cantonese subtitles using standard Chinese "
        "subtitles": "使用标准中文字幕补全缺失的书面粤语字幕",
    },
    "zh-hant": {
        "command-line interface for written Cantonese gap translation": (
            "書面粵語缺口翻譯命令列介面"
        ),
        "This command fills empty written Cantonese subtitle lines using the "
        "corresponding standard Chinese subtitle lines as reference.": (
            "此命令使用對應的標準中文字幕作為參考，補全空白的書面粵語字幕行。"
        ),
        'aligned standard Chinese subtitle infile or "-" for stdin': (
            '已對齊的標準中文字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "script for prompts and output conversion (default: simplified)": (
            "提示詞與輸出轉換使用的字形（預設：簡體）"
        ),
        'written Cantonese subtitle infile with gaps, or "-" for stdin': (
            '含缺口的書面粵語字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        (
            "gap-filled written Cantonese subtitle outfile path (default: stdout)"
        ): "補全缺口後的書面粵語字幕輸出檔路徑（預設：標準輸出）",
        "fill missing written Cantonese subtitles using standard Chinese "
        "subtitles": "使用標準中文字幕補全缺失的書面粵語字幕",
    },
}
"""Localized help text keyed by locale and English source text."""


class YueTranslateVsZhoCli(ScinoephileCliBase):
    """Fill missing written Cantonese subtitles using standard Chinese subtitles."""

    localizations = merge_localizations(
        LLM_LOCALIZATIONS,
        YUE_TRANSLATE_VS_ZHO_LOCALIZATIONS,
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
            help='written Cantonese subtitle infile with gaps, or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--zho-infile",
            dest="zho_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='aligned standard Chinese subtitle infile or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--script",
            default="simplified",
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
            help="gap-filled written Cantonese subtitle outfile path (default: stdout)",
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
        return "translate-vs-zho"

    @classmethod
    def _get_translation_prompt_cls(
        cls, script: str
    ) -> type[YueGappedTranslationVsZhoPromptYueHans]:
        """Get the gap translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            gap translation prompt class
        """
        if script == "traditional":
            return YueGappedTranslationVsZhoPromptYueHant
        return YueGappedTranslationVsZhoPromptYueHans

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        yue_infile_path: Path | str,
        zho_infile_path: Path | str,
        script: str,
        llm_provider_name: str,
        llm_model_name: str | None,
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

        # Perform operations
        prompt_cls = cls._get_translation_prompt_cls(script)
        provider = get_provider(llm_provider_name, model=llm_model_name)
        translator = get_yue_vs_zho_gapped_translator(
            prompt_cls=prompt_cls, provider=provider
        )
        yuewen = get_yue_gapped_translated_vs_zho(
            yuewen=yuewen,
            zhongwen=zhongwen,
            translator=translator,
        )

        # Write outputs
        write_series(
            parser, yuewen, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    YueTranslateVsZhoCli.main()
