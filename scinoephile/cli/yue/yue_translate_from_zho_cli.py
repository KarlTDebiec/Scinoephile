#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese translation from Chinese.

This command translates standard Chinese subtitles into written Cantonese, optionally
filling gaps in written Cantonese subtitles or using written Cantonese guide subtitles.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
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
from scinoephile.multilang.yue_zho.gapped_translation import (
    YueGappedTranslationVsZhoPromptYueHans,
    YueGappedTranslationVsZhoPromptYueHant,
    get_yue_gapped_translated_vs_zho,
    get_yue_vs_zho_gapped_translator,
)
from scinoephile.multilang.yue_zho.guided_translation import (
    YueGuidedTranslationVsZhoPromptYueHans,
    YueGuidedTranslationVsZhoPromptYueHant,
    get_yue_translated_from_zho_with_yue_guidance,
    get_yue_zho_guided_translator,
)
from scinoephile.multilang.yue_zho.translation import (
    YueTranslationVsZhoPromptYueHans,
    YueTranslationVsZhoPromptYueHant,
    get_yue_translated_from_zho,
    get_yue_zho_translator,
)

__all__ = ["YueTranslateFromZhoCli"]

YUE_TRANSLATE_FROM_ZHO_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for written Cantonese translation from Chinese": (
            "从中文翻译书面粤语字幕的命令行界面"
        ),
        "This command translates standard Chinese subtitles into written Cantonese, "
        "optionally filling gaps in written Cantonese subtitles or using written "
        "Cantonese guide subtitles.": (
            "此命令将标准中文字幕翻译为书面粤语，并可选择补全书面粤语字幕缺口"
            "或使用书面粤语参考字幕。"
        ),
        'standard Chinese subtitle infile or "-" for stdin': (
            '标准中文字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "script for prompts and output conversion (default: simplified)": (
            "提示词和输出转换使用的字形（默认：简体）"
        ),
        "written Cantonese subtitle infile with gaps to fill with translation from "
        'standard Chinese, or "-" for stdin': (
            "含缺口、需根据标准中文翻译补全的书面粤语字幕输入文件，或使用 "
            '"-" 表示标准输入'
        ),
        "written Cantonese subtitle infile with which to guide translation from "
        'standard Chinese, or "-" for stdin': (
            '用于指导从标准中文翻译的书面粤语字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "written Cantonese subtitle outfile path (default: stdout)": (
            "书面粤语字幕输出文件路径（默认：标准输出）"
        ),
        "translate written Cantonese subtitles from standard Chinese subtitles": (
            "根据标准中文字幕翻译书面粤语字幕"
        ),
    },
    "zh-hant": {
        "command-line interface for written Cantonese translation from Chinese": (
            "從中文翻譯書面粵語字幕的命令列介面"
        ),
        "This command translates standard Chinese subtitles into written Cantonese, "
        "optionally filling gaps in written Cantonese subtitles or using written "
        "Cantonese guide subtitles.": (
            "此命令將標準中文字幕翻譯為書面粵語，並可選擇補全書面粵語字幕缺口"
            "或使用書面粵語參考字幕。"
        ),
        'standard Chinese subtitle infile or "-" for stdin': (
            '標準中文字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "script for prompts and output conversion (default: simplified)": (
            "提示詞與輸出轉換使用的字形（預設：簡體）"
        ),
        "written Cantonese subtitle infile with gaps to fill with translation from "
        'standard Chinese, or "-" for stdin': (
            "含缺口、需根據標準中文翻譯補全的書面粵語字幕輸入檔，或使用 "
            '"-" 代表標準輸入'
        ),
        "written Cantonese subtitle infile with which to guide translation from "
        'standard Chinese, or "-" for stdin': (
            '用於指導從標準中文翻譯的書面粵語字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "written Cantonese subtitle outfile path (default: stdout)": (
            "書面粵語字幕輸出檔路徑（預設：標準輸出）"
        ),
        "translate written Cantonese subtitles from standard Chinese subtitles": (
            "根據標準中文字幕翻譯書面粵語字幕"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class YueTranslateFromZhoCli(ScinoephileCliBase):
    """Translate written Cantonese subtitles from standard Chinese subtitles."""

    localizations = merge_localizations(
        LLM_LOCALIZATIONS,
        YUE_TRANSLATE_FROM_ZHO_LOCALIZATIONS,
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
            "--zho-infile",
            dest="zho_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='standard Chinese subtitle infile or "-" for stdin',
        )
        yue_input_group = arg_groups["input arguments"].add_mutually_exclusive_group()
        yue_input_group.add_argument(
            "--yue-gapped-infile",
            dest="yue_gapped_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help=(
                "written Cantonese subtitle infile with gaps to fill with translation "
                'from standard Chinese, or "-" for stdin'
            ),
        )
        yue_input_group.add_argument(
            "--yue-guide-infile",
            dest="yue_guide_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help=(
                "written Cantonese subtitle infile with which to guide translation "
                'from standard Chinese, or "-" for stdin'
            ),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--script",
            default="simplified",
            metavar="{simplified,traditional}",
            type=str_arg(options=("simplified", "traditional")),
            help="script for prompts and output conversion (default: simplified)",
        )
        add_llm_provider_arguments(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
            help="written Cantonese subtitle outfile path (default: stdout)",
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
        return "translate-from-zho"

    @classmethod
    def _get_gapped_translation_prompt_cls(
        cls, script: str
    ) -> type[YueGappedTranslationVsZhoPromptYueHans]:
        """Get the gapped translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            gapped translation prompt class
        """
        if script == "traditional":
            return YueGappedTranslationVsZhoPromptYueHant
        return YueGappedTranslationVsZhoPromptYueHans

    @classmethod
    def _get_guided_translation_prompt_cls(
        cls, script: str
    ) -> type[YueGuidedTranslationVsZhoPromptYueHans]:
        """Get the guided translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            guided translation prompt class
        """
        if script == "traditional":
            return YueGuidedTranslationVsZhoPromptYueHant
        return YueGuidedTranslationVsZhoPromptYueHans

    @classmethod
    def _get_translation_prompt_cls(
        cls, script: str
    ) -> type[YueTranslationVsZhoPromptYueHans]:
        """Get the regular translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            regular translation prompt class
        """
        if script == "traditional":
            return YueTranslationVsZhoPromptYueHant
        return YueTranslationVsZhoPromptYueHans

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        zho_infile_path: Path | str,
        yue_gapped_infile_path: Path | str | None,
        yue_guide_infile_path: Path | str | None,
        script: str,
        llm: LlmArguments,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")
        if zho_infile_path == "-" and (
            yue_gapped_infile_path == "-" or yue_guide_infile_path == "-"
        ):
            parser.error(
                "--zho-infile and a written Cantonese infile may not both be '-'"
            )

        # Read inputs
        zhongwen = read_series(parser, zho_infile_path, allow_stdin=True)
        additional_context = read_llm_additional_context(
            parser, llm.additional_context_file_path
        )
        provider = get_provider(llm.provider_name, model=llm.model_name)

        # Perform operations
        if yue_gapped_infile_path is not None:
            yuewen = read_series(parser, yue_gapped_infile_path, allow_stdin=True)
            prompt_cls = cls._get_gapped_translation_prompt_cls(script)
            translator = get_yue_vs_zho_gapped_translator(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            yuewen = get_yue_gapped_translated_vs_zho(
                yuewen=yuewen,
                zhongwen=zhongwen,
                translator=translator,
            )
        elif yue_guide_infile_path is not None:
            yuewen = read_series(parser, yue_guide_infile_path, allow_stdin=True)
            prompt_cls = cls._get_guided_translation_prompt_cls(script)
            translator = get_yue_zho_guided_translator(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            yuewen = get_yue_translated_from_zho_with_yue_guidance(
                zhongwen=zhongwen,
                yuewen=yuewen,
                translator=translator,
            )
        else:
            prompt_cls = cls._get_translation_prompt_cls(script)
            translator = get_yue_zho_translator(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            yuewen = get_yue_translated_from_zho(
                zhongwen=zhongwen,
                translator=translator,
            )

        # Write outputs
        write_series(
            parser, yuewen, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    YueTranslateFromZhoCli.main()
