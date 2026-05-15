#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English translation from Chinese.

This command translates Chinese subtitles into English, optionally filling gaps in
English subtitles or using English guide subtitles.
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
)
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.eng_zho.gapped_translation import (
    get_eng_gapped_translated_vs_zho,
    get_eng_vs_zho_gapped_translator,
)
from scinoephile.multilang.eng_zho.guided_translation import (
    get_eng_translated_from_zho_with_eng_guidance,
    get_eng_zho_guided_translator,
)
from scinoephile.multilang.eng_zho.translation import (
    get_eng_translated_from_zho,
    get_eng_zho_translator,
)

__all__ = ["EngTranslateVsZhoCli"]

ENG_TRANSLATE_VS_ZHO_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for English translation from Chinese": (
            "从中文翻译英文字幕的命令行界面"
        ),
        "This command translates Chinese subtitles into English, optionally "
        "filling gaps in English subtitles or using English guide subtitles.": (
            "此命令将中文字幕翻译为英文，并可选择补全英文字幕缺口或使用英文参考字幕。"
        ),
        'Chinese subtitle infile or "-" for stdin': (
            '中文字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "English subtitle infile with gaps to fill with translation from Chinese, "
        'or "-" for stdin': (
            '含缺口、需根据中文翻译补全的英文字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "English subtitle infile with which to guide translation from Chinese, "
        'or "-" for stdin': (
            '用于指导从中文翻译的英文字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "English subtitle outfile path (default: stdout)": (
            "英文字幕输出文件路径（默认：标准输出）"
        ),
        "translate English subtitles from Chinese subtitles": (
            "根据中文字幕翻译英文字幕"
        ),
    },
    "zh-hant": {
        "command-line interface for English translation from Chinese": (
            "從中文翻譯英文字幕的命令列介面"
        ),
        "This command translates Chinese subtitles into English, optionally "
        "filling gaps in English subtitles or using English guide subtitles.": (
            "此命令將中文字幕翻譯為英文，並可選擇補全英文字幕缺口或使用英文參考字幕。"
        ),
        'Chinese subtitle infile or "-" for stdin': (
            '中文字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "English subtitle infile with gaps to fill with translation from Chinese, "
        'or "-" for stdin': (
            '含缺口、需根據中文翻譯補全的英文字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "English subtitle infile with which to guide translation from Chinese, "
        'or "-" for stdin': (
            '用於指導從中文翻譯的英文字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "English subtitle outfile path (default: stdout)": (
            "英文字幕輸出檔路徑（預設：標準輸出）"
        ),
        "translate English subtitles from Chinese subtitles": (
            "根據中文字幕翻譯英文字幕"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class EngTranslateVsZhoCli(ScinoephileCliBase):
    """Translate English subtitles from Chinese subtitles."""

    localizations = merge_localizations(
        LLM_LOCALIZATIONS,
        ENG_TRANSLATE_VS_ZHO_LOCALIZATIONS,
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
            "--zho-infile",
            dest="zho_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='Chinese subtitle infile or "-" for stdin',
        )
        eng_input_group = arg_groups["input arguments"].add_mutually_exclusive_group()
        eng_input_group.add_argument(
            "--eng-gapped-infile",
            dest="eng_gapped_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help=(
                "English subtitle infile with gaps to fill with translation from "
                'Chinese, or "-" for stdin'
            ),
        )
        eng_input_group.add_argument(
            "--eng-guide-infile",
            dest="eng_guide_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help=(
                "English subtitle infile with which to guide translation from "
                'Chinese, or "-" for stdin'
            ),
        )

        # Operation arguments
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
            help="English subtitle outfile path (default: stdout)",
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
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        zho_infile_path: Path | str,
        eng_gapped_infile_path: Path | str | None,
        eng_guide_infile_path: Path | str | None,
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
        if zho_infile_path == "-" and (
            eng_gapped_infile_path == "-" or eng_guide_infile_path == "-"
        ):
            parser.error("--zho-infile and an English infile may not both be '-'")

        # Read inputs
        zho = read_series(parser, zho_infile_path, allow_stdin=True)
        additional_context = read_llm_additional_context(
            parser, llm_additional_context_file_path
        )
        provider = get_provider(llm_provider_name, model=llm_model_name)

        # Perform operations
        if eng_gapped_infile_path is not None:
            eng = read_series(parser, eng_gapped_infile_path, allow_stdin=True)
            translator = get_eng_vs_zho_gapped_translator(
                provider=provider,
                additional_context=additional_context,
            )
            eng = get_eng_gapped_translated_vs_zho(
                eng=eng,
                zho=zho,
                translator=translator,
            )
        elif eng_guide_infile_path is not None:
            eng = read_series(parser, eng_guide_infile_path, allow_stdin=True)
            translator = get_eng_zho_guided_translator(
                provider=provider,
                additional_context=additional_context,
            )
            eng = get_eng_translated_from_zho_with_eng_guidance(
                zho=zho,
                eng=eng,
                translator=translator,
            )
        else:
            translator = get_eng_zho_translator(
                provider=provider,
                additional_context=additional_context,
            )
            eng = get_eng_translated_from_zho(zho=zho, translator=translator)

        # Write outputs
        write_series(
            parser, eng, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    EngTranslateVsZhoCli.main()
