#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for standard Chinese translation from written Cantonese.

This command translates written Cantonese subtitles into standard Chinese, optionally
filling gaps in standard Chinese subtitles or using standard Chinese guide subtitles.
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
from scinoephile.multilang.zho_yue.gapped_translation import (
    ZhoGappedTranslationVsYuePromptZhoHans,
    ZhoGappedTranslationVsYuePromptZhoHant,
    get_zho_gapped_translated_vs_yue,
    get_zho_vs_yue_gapped_translator,
)
from scinoephile.multilang.zho_yue.guided_translation import (
    ZhoGuidedTranslationVsYuePromptZhoHans,
    ZhoGuidedTranslationVsYuePromptZhoHant,
    get_zho_translated_from_yue_with_zho_guidance,
    get_zho_yue_guided_translator,
)
from scinoephile.multilang.zho_yue.translation import (
    ZhoTranslationVsYuePromptZhoHans,
    ZhoTranslationVsYuePromptZhoHant,
    get_zho_translated_from_yue,
    get_zho_yue_translator,
)

__all__ = ["ZhoTranslateFromYueCli"]

ZHO_TRANSLATE_FROM_YUE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for standard Chinese translation from written "
        "Cantonese": "从书面粤语翻译标准中文字幕的命令行界面",
        "This command translates written Cantonese subtitles into standard Chinese, "
        "optionally filling gaps in standard Chinese subtitles or using standard "
        "Chinese guide subtitles.": (
            "此命令将书面粤语字幕翻译为标准中文，并可选择补全标准中文字幕缺口"
            "或使用标准中文参考字幕。"
        ),
        'written Cantonese subtitle infile or "-" for stdin': (
            '书面粤语字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "script for prompts and output conversion (default: simplified)": (
            "提示词和输出转换使用的字形（默认：简体）"
        ),
        "standard Chinese subtitle infile with gaps to fill with translation from "
        'written Cantonese, or "-" for stdin': (
            "含缺口、需根据书面粤语翻译补全的标准中文字幕输入文件，或使用 "
            '"-" 表示标准输入'
        ),
        "standard Chinese subtitle infile with which to guide translation from "
        'written Cantonese, or "-" for stdin': (
            '用于指导从书面粤语翻译的标准中文字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "standard Chinese subtitle outfile path (default: stdout)": (
            "标准中文字幕输出文件路径（默认：标准输出）"
        ),
        "translate standard Chinese subtitles from written Cantonese subtitles": (
            "根据书面粤语字幕翻译标准中文字幕"
        ),
    },
    "zh-hant": {
        "command-line interface for standard Chinese translation from written "
        "Cantonese": "從書面粵語翻譯標準中文字幕的命令列介面",
        "This command translates written Cantonese subtitles into standard Chinese, "
        "optionally filling gaps in standard Chinese subtitles or using standard "
        "Chinese guide subtitles.": (
            "此命令將書面粵語字幕翻譯為標準中文，並可選擇補全標準中文字幕缺口"
            "或使用標準中文參考字幕。"
        ),
        'written Cantonese subtitle infile or "-" for stdin': (
            '書面粵語字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "script for prompts and output conversion (default: simplified)": (
            "提示詞與輸出轉換使用的字形（預設：簡體）"
        ),
        "standard Chinese subtitle infile with gaps to fill with translation from "
        'written Cantonese, or "-" for stdin': (
            "含缺口、需根據書面粵語翻譯補全的標準中文字幕輸入檔，或使用 "
            '"-" 代表標準輸入'
        ),
        "standard Chinese subtitle infile with which to guide translation from "
        'written Cantonese, or "-" for stdin': (
            '用於指導從書面粵語翻譯的標準中文字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "standard Chinese subtitle outfile path (default: stdout)": (
            "標準中文字幕輸出檔路徑（預設：標準輸出）"
        ),
        "translate standard Chinese subtitles from written Cantonese subtitles": (
            "根據書面粵語字幕翻譯標準中文字幕"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class ZhoTranslateFromYueCli(ScinoephileCliBase):
    """Translate standard Chinese subtitles from written Cantonese subtitles."""

    localizations = merge_localizations(
        LLM_LOCALIZATIONS,
        ZHO_TRANSLATE_FROM_YUE_LOCALIZATIONS,
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
            "--yue-infile",
            dest="yue_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='written Cantonese subtitle infile or "-" for stdin',
        )
        zho_input_group = arg_groups["input arguments"].add_mutually_exclusive_group()
        zho_input_group.add_argument(
            "--zho-gapped-infile",
            dest="zho_gapped_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help=(
                "standard Chinese subtitle infile with gaps to fill with translation "
                'from written Cantonese, or "-" for stdin'
            ),
        )
        zho_input_group.add_argument(
            "--zho-guide-infile",
            dest="zho_guide_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help=(
                "standard Chinese subtitle infile with which to guide translation "
                'from written Cantonese, or "-" for stdin'
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
            help="standard Chinese subtitle outfile path (default: stdout)",
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
        return "translate-from-yue"

    @classmethod
    def _get_gapped_translation_prompt_cls(
        cls, script: str
    ) -> type[ZhoGappedTranslationVsYuePromptZhoHans]:
        """Get the gapped translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            gapped translation prompt class
        """
        if script == "traditional":
            return ZhoGappedTranslationVsYuePromptZhoHant
        return ZhoGappedTranslationVsYuePromptZhoHans

    @classmethod
    def _get_guided_translation_prompt_cls(
        cls, script: str
    ) -> type[ZhoGuidedTranslationVsYuePromptZhoHans]:
        """Get the guided translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            guided translation prompt class
        """
        if script == "traditional":
            return ZhoGuidedTranslationVsYuePromptZhoHant
        return ZhoGuidedTranslationVsYuePromptZhoHans

    @classmethod
    def _get_translation_prompt_cls(
        cls, script: str
    ) -> type[ZhoTranslationVsYuePromptZhoHans]:
        """Get the regular translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            regular translation prompt class
        """
        if script == "traditional":
            return ZhoTranslationVsYuePromptZhoHant
        return ZhoTranslationVsYuePromptZhoHans

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        yue_infile_path: Path | str,
        zho_gapped_infile_path: Path | str | None,
        zho_guide_infile_path: Path | str | None,
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
        if yue_infile_path == "-" and (
            zho_gapped_infile_path == "-" or zho_guide_infile_path == "-"
        ):
            parser.error(
                "--yue-infile and a standard Chinese infile may not both be '-'"
            )

        # Read inputs
        yuewen = read_series(parser, yue_infile_path, allow_stdin=True)
        additional_context = read_llm_additional_context(
            parser, llm.additional_context_file_path
        )
        provider = get_provider(llm.provider_name, model=llm.model_name)

        # Perform operations
        if zho_gapped_infile_path is not None:
            zhongwen = read_series(parser, zho_gapped_infile_path, allow_stdin=True)
            prompt_cls = cls._get_gapped_translation_prompt_cls(script)
            translator = get_zho_vs_yue_gapped_translator(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            zhongwen = get_zho_gapped_translated_vs_yue(
                zhongwen=zhongwen,
                yuewen=yuewen,
                translator=translator,
            )
        elif zho_guide_infile_path is not None:
            zhongwen = read_series(parser, zho_guide_infile_path, allow_stdin=True)
            prompt_cls = cls._get_guided_translation_prompt_cls(script)
            translator = get_zho_yue_guided_translator(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            zhongwen = get_zho_translated_from_yue_with_zho_guidance(
                yuewen=yuewen,
                zhongwen=zhongwen,
                translator=translator,
            )
        else:
            prompt_cls = cls._get_translation_prompt_cls(script)
            translator = get_zho_yue_translator(
                prompt_cls=prompt_cls,
                provider=provider,
                additional_context=additional_context,
            )
            zhongwen = get_zho_translated_from_yue(
                yuewen=yuewen,
                translator=translator,
            )

        # Write outputs
        write_series(
            parser,
            zhongwen,
            outfile_path if outfile_path is not None else "-",
            overwrite,
        )


if __name__ == "__main__":
    ZhoTranslateFromYueCli.main()
