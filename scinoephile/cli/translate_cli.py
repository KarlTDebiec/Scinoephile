#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle translation.

Translate subtitles between supported languages.
"""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

from scinoephile.cli.helpers.io import read_series, write_series
from scinoephile.cli.helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
    read_llm_additional_context,
)
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
from scinoephile.core.subtitles import Series
from scinoephile.lang.id import get_series_language
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.translation import TranslationMode, translate_series

__all__ = ["TranslateCli"]

logger = getLogger(__name__)

TRANSLATE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for subtitle translation": "字幕翻译命令行界面",
        "Translate subtitles between supported languages.": (
            "在受支持的语言之间翻译字幕。"
        ),
        'source subtitle infile or "-" for stdin': (
            '源字幕输入文件，或使用 "-" 表示标准输入'
        ),
        'target-language subtitle infile with gaps to fill, or "-" for stdin': (
            '含缺口、需补全的目标语言字幕输入文件，或使用 "-" 表示标准输入'
        ),
        'target-language subtitle infile with which to guide translation, or "-" '
        "for stdin": ('用于指导翻译的目标语言字幕输入文件，或使用 "-" 表示标准输入'),
        "source language tag (detected from infile if omitted)": (
            "源语言标签（省略时从输入文件检测）"
        ),
        "target language tag (required unless guide or gapped input is detected)": (
            "目标语言标签（除非可从参考或缺口输入检测，否则必填）"
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
        'target-language subtitle infile with gaps to fill, or "-" for stdin': (
            '含缺口、需補全的目標語言字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        'target-language subtitle infile with which to guide translation, or "-" '
        "for stdin": ('用於指導翻譯的目標語言字幕輸入檔，或使用 "-" 代表標準輸入'),
        "source language tag (detected from infile if omitted)": (
            "來源語言標籤（省略時從輸入檔偵測）"
        ),
        "target language tag (required unless guide or gapped input is detected)": (
            "目標語言標籤（除非可從參考或缺口輸入偵測，否則必填）"
        ),
        "subtitle outfile path (default: stdout)": ("字幕輸出檔路徑（預設：標準輸出）"),
        "translate subtitles between supported languages": ("在支援的語言之間翻譯字幕"),
    },
}
"""Localized help text keyed by locale and English source text."""


class TranslateCli(ScinoephileCliBase):
    """Translate subtitles between supported languages."""

    localizations = merge_localizations(
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
            default=None,
            type=input_file_arg(allow_stdin=True),
            help='target-language subtitle infile with gaps to fill, or "-" for stdin',
        )
        target_input_group.add_argument(
            "--guide-infile",
            dest="guide_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help=(
                "target-language subtitle infile with which to guide translation, "
                'or "-" for stdin'
            ),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--source-language",
            default=None,
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="source language tag (detected from infile if omitted)",
        )
        arg_groups["operation arguments"].add_argument(
            "--target-language",
            default=None,
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help=(
                "target language tag (required unless guide or gapped input "
                "is detected)"
            ),
        )
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
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
        llm_args: LlmArguments,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")
        target_infile_path, mode = cls._get_target_infile_and_mode(
            gapped_infile_path=gapped_infile_path,
            guide_infile_path=guide_infile_path,
        )
        cls._validate_stdin_inputs(
            parser,
            infile_path=infile_path,
            target_infile_path=target_infile_path,
        )

        # Read inputs and resolve languages
        source = read_series(parser, infile_path, allow_stdin=True)
        target = None
        if target_infile_path is not None:
            target = read_series(parser, target_infile_path, allow_stdin=True)
        source_language = cls._resolve_language(
            parser=parser,
            series=source,
            explicit_language=source_language,
            role_name="source",
            option_name="--source-language",
        )
        target_language = cls._resolve_target_language(
            parser=parser,
            target=target,
            explicit_language=target_language,
        )
        additional_context = read_llm_additional_context(
            parser, llm_args.additional_context_file_path
        )
        provider = get_provider(llm_args.provider_name, model=llm_args.model_name)

        # Perform operation
        try:
            output = translate_series(
                source=source,
                source_language=source_language,
                target_language=target_language,
                mode=mode,
                target=target,
                provider=provider,
                additional_context=additional_context,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        write_series(
            parser, output, outfile_path if outfile_path is not None else "-", overwrite
        )

    @staticmethod
    def _get_target_infile_and_mode(
        *,
        gapped_infile_path: Path | str | None,
        guide_infile_path: Path | str | None,
    ) -> tuple[Path | str | None, TranslationMode]:
        """Get target-language input path and translation mode.

        Arguments:
            gapped_infile_path: target-language gapped subtitle path
            guide_infile_path: target-language guide subtitle path
        Returns:
            target-language input path and translation mode
        """
        if gapped_infile_path is not None:
            return gapped_infile_path, "gapped"
        if guide_infile_path is not None:
            return guide_infile_path, "guided"
        return None, "regular"

    @staticmethod
    def _resolve_language(
        *,
        parser: ArgumentParser,
        series: Series,
        explicit_language: Language | None,
        role_name: str,
        option_name: str,
    ) -> Language:
        """Resolve a detected or explicit language for a series.

        Arguments:
            parser: parser used for user-facing error output
            series: subtitle series to classify
            explicit_language: explicit language argument, if provided
            role_name: user-facing role name
            option_name: option to recommend when detection fails
        Returns:
            resolved language
        """
        detected_language = get_series_language(series)
        if explicit_language is not None:
            if (
                detected_language is not None
                and detected_language is not explicit_language
            ):
                logger.warning(
                    f"Explicit {role_name} language {explicit_language.tag} does not "
                    f"match detected {role_name} language {detected_language.tag}; "
                    f"using {explicit_language.tag}"
                )
            return explicit_language
        if detected_language is None:
            parser.error(
                f"Unable to determine {role_name} language; pass {option_name}"
            )
        return detected_language

    @classmethod
    def _resolve_target_language(
        cls,
        *,
        parser: ArgumentParser,
        target: Series | None,
        explicit_language: Language | None,
    ) -> Language:
        """Resolve target language from an argument or target-language input.

        Arguments:
            parser: parser used for user-facing error output
            target: target-language guide or gapped subtitle series
            explicit_language: explicit target language argument, if provided
        Returns:
            resolved target language
        """
        if target is not None:
            return cls._resolve_language(
                parser=parser,
                series=target,
                explicit_language=explicit_language,
                role_name="target",
                option_name="--target-language",
            )
        if explicit_language is None:
            parser.error(
                "--target-language is required unless --guide-infile or "
                "--gapped-infile can determine target language"
            )
        return explicit_language

    @staticmethod
    def _validate_stdin_inputs(
        parser: ArgumentParser,
        *,
        infile_path: Path | str,
        target_infile_path: Path | str | None,
    ):
        """Validate stdin is used for at most one input stream.

        Arguments:
            parser: parser used for user-facing error output
            infile_path: source subtitle path
            target_infile_path: target-language subtitle path, if provided
        """
        if str(infile_path) == "-" and str(target_infile_path) == "-":
            parser.error("source and target-language inputs may not both be '-'")


if __name__ == "__main__":
    TranslateCli.main()
