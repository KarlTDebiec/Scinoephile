#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for standard, gapped, and guided translation audits."""

from __future__ import annotations

from argparse import ArgumentParser
from enum import StrEnum
from pathlib import Path

from scinoephile.analysis.audit.gap_translation import (
    GapTranslationAuditFilter,
    audit_gap_translation,
)
from scinoephile.analysis.audit.translation import (
    TranslationAuditFilter,
    audit_guided_translation,
    audit_translation,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.llms.gap_translation import GapTranslationManager
from scinoephile.llms.guided_translation import GuidedTranslationManager
from scinoephile.llms.translation import TranslationManager

from .audit_cli_base import AuditCliBase

__all__ = ["AuditTranslationCli"]

AUDIT_TRANSLATION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit standard, gapped, or guided subtitle translations": (
            "审核标准、缺口或引导式字幕翻译"
        ),
        (
            "translation workflow to audit: standard, gapped, or guided "
            "(default: standard)"
        ): ("要审核的翻译工作流：standard、gapped 或 guided（默认：standard）"),
        "source subtitle SRT file used for standard or guided translation": (
            "用于标准或引导式翻译的源字幕 SRT 文件"
        ),
        "gapped target subtitle SRT file used for gapped translation": (
            "用于缺口翻译的含缺失项目标字幕 SRT 文件"
        ),
        "guide subtitle SRT file used for gapped or guided translation": (
            "用于缺口或引导式翻译的参考字幕 SRT 文件"
        ),
        "translation test-case JSON file for the selected workflow": (
            "所选工作流的翻译测试用例 JSON 文件"
        ),
        "rows to include: all or unverified (default: all)": (
            "要包含的行：all 表示全部，unverified 表示未验证（默认：all）"
        ),
    },
    "zh-hant": {
        "audit standard, gapped, or guided subtitle translations": (
            "稽核標準、缺口或引導式字幕翻譯"
        ),
        (
            "translation workflow to audit: standard, gapped, or guided "
            "(default: standard)"
        ): ("要稽核的翻譯工作流程：standard、gapped 或 guided（預設：standard）"),
        "source subtitle SRT file used for standard or guided translation": (
            "用於標準或引導式翻譯的來源字幕 SRT 檔"
        ),
        "gapped target subtitle SRT file used for gapped translation": (
            "用於缺口翻譯的含缺失項目標字幕 SRT 檔"
        ),
        "guide subtitle SRT file used for gapped or guided translation": (
            "用於缺口或引導式翻譯的參考字幕 SRT 檔"
        ),
        "translation test-case JSON file for the selected workflow": (
            "所選工作流程的翻譯測試案例 JSON 檔"
        ),
        "rows to include: all or unverified (default: all)": (
            "要包含的列：all 表示全部，unverified 表示未驗證（預設：all）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class _TranslationAuditMode(StrEnum):
    """Translation workflows supported by the unified audit command."""

    gapped = "gapped"
    """Audit translations generated for gaps in an existing target track."""
    guided = "guided"
    """Audit translations generated with target-language guide subtitles."""
    standard = "standard"
    """Audit standard source-to-target translations."""


class AuditTranslationCli(AuditCliBase):
    """Audit standard, gapped, or guided subtitle translations."""

    localizations = AUDIT_TRANSLATION_LOCALIZATIONS
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
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--source",
            dest="source_path",
            type=input_file_arg(),
            help="source subtitle SRT file used for standard or guided translation",
        )
        arg_groups["input arguments"].add_argument(
            "--target",
            dest="target_path",
            type=input_file_arg(),
            help="gapped target subtitle SRT file used for gapped translation",
        )
        arg_groups["input arguments"].add_argument(
            "--guide",
            dest="guide_path",
            type=input_file_arg(),
            help="guide subtitle SRT file used for gapped or guided translation",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            required=True,
            type=input_file_arg(),
            help="translation test-case JSON file for the selected workflow",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--mode",
            choices=tuple(_TranslationAuditMode),
            default=_TranslationAuditMode.standard,
            type=enum_arg(_TranslationAuditMode),
            help=(
                "translation workflow to audit: standard, gapped, or guided "
                "(default: standard)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--filter",
            choices=tuple(TranslationAuditFilter),
            default=TranslationAuditFilter.all,
            dest="row_filter",
            metavar="{all,unverified}",
            type=enum_arg(TranslationAuditFilter),
            help="rows to include: all or unverified (default: all)",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "translation"

    @classmethod
    def _audit_gapped(
        cls,
        parser: ArgumentParser,
        target_path: Path,
        guide_path: Path,
        json_path: Path,
        *,
        row_filter: TranslationAuditFilter,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
    ) -> str:
        """Load and audit one gapped-translation workflow.

        Arguments:
            parser: parser used to report user-facing errors
            target_path: gapped target subtitle SRT path
            guide_path: complete guide subtitle SRT path
            json_path: gap-translation test-case JSON path
            row_filter: rows to include in the report
            first_index: first guide subtitle number to include
            last_index: last guide subtitle number to include
            first_block: first paired block number to include
            last_block: last paired block number to include
        Returns:
            Markdown audit report
        """
        # Read inputs
        target = read_series(parser, target_path)
        guide = read_series(parser, guide_path)
        test_cases = cls.load_test_cases(
            parser,
            json_path,
            GapTranslationManager,
            workflow_name="gapped translation",
        )

        # Perform operation
        return audit_gap_translation(
            target,
            guide,
            test_cases,
            row_filter=GapTranslationAuditFilter(row_filter.value),
            first_index=first_index,
            last_index=last_index,
            first_block=first_block,
            last_block=last_block,
        )

    @classmethod
    def _audit_guided(
        cls,
        parser: ArgumentParser,
        source_path: Path,
        guide_path: Path,
        json_path: Path,
        *,
        row_filter: TranslationAuditFilter,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
    ) -> str:
        """Load and audit one guided-translation workflow.

        Arguments:
            parser: parser used to report user-facing errors
            source_path: source subtitle SRT path
            guide_path: target-language guide subtitle SRT path
            json_path: guided-translation test-case JSON path
            row_filter: rows to include in the report
            first_index: first source subtitle number to include
            last_index: last source subtitle number to include
            first_block: first paired block number to include
            last_block: last paired block number to include
        Returns:
            Markdown audit report
        """
        # Read inputs
        source = read_series(parser, source_path)
        guide = read_series(parser, guide_path)
        test_cases = cls.load_test_cases(
            parser,
            json_path,
            GuidedTranslationManager,
            workflow_name="guided translation",
        )

        # Perform operation
        return audit_guided_translation(
            source,
            guide,
            test_cases,
            row_filter=row_filter,
            first_index=first_index,
            last_index=last_index,
            first_block=first_block,
            last_block=last_block,
        )

    @classmethod
    def _audit_standard(
        cls,
        parser: ArgumentParser,
        source_path: Path,
        json_path: Path,
        *,
        row_filter: TranslationAuditFilter,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
    ) -> str:
        """Load and audit one standard-translation workflow.

        Arguments:
            parser: parser used to report user-facing errors
            source_path: source subtitle SRT path
            json_path: translation test-case JSON path
            row_filter: rows to include in the report
            first_index: first source subtitle number to include
            last_index: last source subtitle number to include
            first_block: first source block number to include
            last_block: last source block number to include
        Returns:
            Markdown audit report
        """
        # Read inputs
        source = read_series(parser, source_path)
        test_cases = cls.load_test_cases(
            parser,
            json_path,
            TranslationManager,
            workflow_name="standard translation",
        )

        # Perform operation
        return audit_translation(
            source,
            test_cases,
            row_filter=row_filter,
            first_index=first_index,
            last_index=last_index,
            first_block=first_block,
            last_block=last_block,
        )

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        source_path: Path | None,
        target_path: Path | None,
        guide_path: Path | None,
        json_path: Path,
        mode: _TranslationAuditMode,
        row_filter: TranslationAuditFilter,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments.

        Arguments:
            _parser: parser used to report user-facing errors
            source_path: optional source subtitle SRT path
            target_path: optional gapped target subtitle SRT path
            guide_path: optional guide subtitle SRT path
            json_path: translation test-case JSON path
            mode: translation workflow to audit
            row_filter: rows to include in the report
            first_index: first workflow subtitle number to include
            last_index: last workflow subtitle number to include
            first_block: first workflow block number to include
            last_block: last workflow block number to include
            outfile_path: optional Markdown output path
            overwrite: whether to overwrite an existing output file
        """
        # Validate arguments
        parser = _parser or cls.argparser()
        cls._validate_mode_inputs(
            parser,
            mode,
            source_path=source_path,
            target_path=target_path,
            guide_path=guide_path,
        )

        # Perform operation
        try:
            if mode is _TranslationAuditMode.standard:
                assert source_path is not None
                report = cls._audit_standard(
                    parser,
                    source_path,
                    json_path,
                    row_filter=row_filter,
                    first_index=first_index,
                    last_index=last_index,
                    first_block=first_block,
                    last_block=last_block,
                )
            elif mode is _TranslationAuditMode.gapped:
                assert target_path is not None and guide_path is not None
                report = cls._audit_gapped(
                    parser,
                    target_path,
                    guide_path,
                    json_path,
                    row_filter=row_filter,
                    first_index=first_index,
                    last_index=last_index,
                    first_block=first_block,
                    last_block=last_block,
                )
            else:
                assert source_path is not None and guide_path is not None
                report = cls._audit_guided(
                    parser,
                    source_path,
                    guide_path,
                    json_path,
                    row_filter=row_filter,
                    first_index=first_index,
                    last_index=last_index,
                    first_block=first_block,
                    last_block=last_block,
                )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        cls.write_report(parser, report, outfile_path, overwrite)

    @staticmethod
    def _validate_mode_inputs(
        parser: ArgumentParser,
        mode: _TranslationAuditMode,
        *,
        source_path: Path | None,
        target_path: Path | None,
        guide_path: Path | None,
    ):
        """Validate mode-specific translation input paths.

        Arguments:
            parser: parser used to report user-facing errors
            mode: translation workflow to audit
            source_path: optional source subtitle SRT path
            target_path: optional gapped target subtitle SRT path
            guide_path: optional guide subtitle SRT path
        """
        # Validate required inputs
        required = {
            _TranslationAuditMode.standard: ((source_path, "--source"),),
            _TranslationAuditMode.gapped: (
                (target_path, "--target"),
                (guide_path, "--guide"),
            ),
            _TranslationAuditMode.guided: (
                (source_path, "--source"),
                (guide_path, "--guide"),
            ),
        }
        for path, option in required[mode]:
            if path is None:
                parser.error(f"{option} is required in {mode.value} mode")

        # Validate unsupported inputs
        unsupported = {
            _TranslationAuditMode.standard: (
                (target_path, "--target"),
                (guide_path, "--guide"),
            ),
            _TranslationAuditMode.gapped: ((source_path, "--source"),),
            _TranslationAuditMode.guided: ((target_path, "--target"),),
        }
        for path, option in unsupported[mode]:
            if path is not None:
                parser.error(f"{option} is not supported in {mode.value} mode")


if __name__ == "__main__":
    AuditTranslationCli.main()
