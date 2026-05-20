#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese translation from English.

This command translates English subtitles into written Cantonese, optionally filling
gaps in written Cantonese subtitles or using written Cantonese guide subtitles.
"""

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
from scinoephile.multilang.yue_eng.gapped_translation import (
    YueGappedTranslationVsEngPromptYueHans,
    YueGappedTranslationVsEngPromptYueHant,
    get_yue_gapped_translated_vs_eng,
    get_yue_vs_eng_gapped_translator,
)
from scinoephile.multilang.yue_eng.guided_translation import (
    YueGuidedTranslationVsEngPromptYueHans,
    YueGuidedTranslationVsEngPromptYueHant,
    get_yue_eng_guided_translator,
    get_yue_translated_from_eng_with_yue_guidance,
)
from scinoephile.multilang.yue_eng.translation import (
    YueTranslationVsEngPromptYueHans,
    YueTranslationVsEngPromptYueHant,
    get_yue_eng_translator,
    get_yue_translated_from_eng,
)

__all__ = ["YueTranslateVsEngCli"]

YUE_TRANSLATE_VS_ENG_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for written Cantonese translation from English": (
            "从英文翻译书面粤语字幕的命令行界面"
        ),
        "This command translates English subtitles into written Cantonese, optionally "
        "filling gaps in written Cantonese subtitles or using written Cantonese guide "
        "subtitles.": (
            "此命令将英文字幕翻译为书面粤语，并可选择补全书面粤语字幕缺口"
            "或使用书面粤语参考字幕。"
        ),
        'English subtitle infile or "-" for stdin': (
            '英文字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "script for prompts and output conversion (default: simplified)": (
            "提示词和输出转换使用的字形（默认：简体）"
        ),
        "written Cantonese subtitle infile with gaps to fill with translation from "
        'English, or "-" for stdin': (
            '含缺口、需根据英文翻译补全的书面粤语字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "written Cantonese subtitle infile with which to guide translation from "
        'English, or "-" for stdin': (
            '用于指导从英文翻译的书面粤语字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "written Cantonese subtitle outfile path (default: stdout)": (
            "书面粤语字幕输出文件路径（默认：标准输出）"
        ),
        "translate written Cantonese subtitles from English subtitles": (
            "根据英文字幕翻译书面粤语字幕"
        ),
    },
    "zh-hant": {
        "command-line interface for written Cantonese translation from English": (
            "從英文翻譯書面粵語字幕的命令列介面"
        ),
        "This command translates English subtitles into written Cantonese, optionally "
        "filling gaps in written Cantonese subtitles or using written Cantonese guide "
        "subtitles.": (
            "此命令將英文字幕翻譯為書面粵語，並可選擇補全書面粵語字幕缺口"
            "或使用書面粵語參考字幕。"
        ),
        'English subtitle infile or "-" for stdin': (
            '英文字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "script for prompts and output conversion (default: simplified)": (
            "提示詞與輸出轉換使用的字形（預設：簡體）"
        ),
        "written Cantonese subtitle infile with gaps to fill with translation from "
        'English, or "-" for stdin': (
            '含缺口、需根據英文翻譯補全的書面粵語字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "written Cantonese subtitle infile with which to guide translation from "
        'English, or "-" for stdin': (
            '用於指導從英文翻譯的書面粵語字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "written Cantonese subtitle outfile path (default: stdout)": (
            "書面粵語字幕輸出檔路徑（預設：標準輸出）"
        ),
        "translate written Cantonese subtitles from English subtitles": (
            "根據英文字幕翻譯書面粵語字幕"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class YueTranslateVsEngCli(ScinoephileCliBase):
    """Translate written Cantonese subtitles from English subtitles."""

    localizations = merge_localizations(
        LLM_LOCALIZATIONS,
        YUE_TRANSLATE_VS_ENG_LOCALIZATIONS,
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
            "--eng-infile",
            dest="eng_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='English subtitle infile or "-" for stdin',
        )
        yue_input_group = arg_groups["input arguments"].add_mutually_exclusive_group()
        yue_input_group.add_argument(
            "--yue-gapped-infile",
            dest="yue_gapped_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help=(
                "written Cantonese subtitle infile with gaps to fill with translation "
                'from English, or "-" for stdin'
            ),
        )
        yue_input_group.add_argument(
            "--yue-guide-infile",
            dest="yue_guide_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help=(
                "written Cantonese subtitle infile with which to guide translation "
                'from English, or "-" for stdin'
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
            arg_groups["operation arguments"], arg_groups["additional help"]
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
        return "translate-from-eng"

    @classmethod
    def _get_gapped_translation_prompt_cls(
        cls, script: str
    ) -> type[YueGappedTranslationVsEngPromptYueHans]:
        """Get the gapped translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            gapped translation prompt class
        """
        if script == "traditional":
            return YueGappedTranslationVsEngPromptYueHant
        return YueGappedTranslationVsEngPromptYueHans

    @classmethod
    def _get_guided_translation_prompt_cls(
        cls, script: str
    ) -> type[YueGuidedTranslationVsEngPromptYueHans]:
        """Get the guided translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            guided translation prompt class
        """
        if script == "traditional":
            return YueGuidedTranslationVsEngPromptYueHant
        return YueGuidedTranslationVsEngPromptYueHans

    @classmethod
    def _get_translation_prompt_cls(
        cls, script: str
    ) -> type[YueTranslationVsEngPromptYueHans]:
        """Get the regular translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            regular translation prompt class
        """
        if script == "traditional":
            return YueTranslationVsEngPromptYueHant
        return YueTranslationVsEngPromptYueHans

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        eng_infile_path: Path | str,
        yue_gapped_infile_path: Path | str | None,
        yue_guide_infile_path: Path | str | None,
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
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")
        if eng_infile_path == "-" and (
            yue_gapped_infile_path == "-" or yue_guide_infile_path == "-"
        ):
            parser.error(
                "--eng-infile and a written Cantonese infile may not both be '-'"
            )

        # Read inputs
        eng = read_series(parser, eng_infile_path, allow_stdin=True)
        additional_context = read_llm_additional_context(
            parser, llm_additional_context_file_path
        )
        provider = get_provider(llm_provider_name, model=llm_model_name)

        # Perform operations
        if yue_gapped_infile_path is not None:
            yuewen = read_series(parser, yue_gapped_infile_path, allow_stdin=True)
            prompt_cls = cls._get_gapped_translation_prompt_cls(script)
            translator = get_yue_vs_eng_gapped_translator(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            yuewen = get_yue_gapped_translated_vs_eng(
                yuewen=yuewen,
                eng=eng,
                translator=translator,
            )
        elif yue_guide_infile_path is not None:
            yuewen = read_series(parser, yue_guide_infile_path, allow_stdin=True)
            prompt_cls = cls._get_guided_translation_prompt_cls(script)
            translator = get_yue_eng_guided_translator(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            yuewen = get_yue_translated_from_eng_with_yue_guidance(
                eng=eng,
                yuewen=yuewen,
                translator=translator,
            )
        else:
            prompt_cls = cls._get_translation_prompt_cls(script)
            translator = get_yue_eng_translator(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            yuewen = get_yue_translated_from_eng(
                eng=eng,
                translator=translator,
            )

        # Write outputs
        write_series(
            parser, yuewen, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    YueTranslateVsEngCli.main()
