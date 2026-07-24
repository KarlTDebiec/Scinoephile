#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for standard, gapped, and guided translation audits."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.analysis.audit.gap_translation import audit_gap_translation
from scinoephile.analysis.audit.guided_translation import audit_guided_translation
from scinoephile.analysis.audit.translation import (
    TranslationAuditFilter,
    audit_translation,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
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
        "source subtitle SRT file used for standard or guided translation": (
            "用于标准或引导式翻译的源字幕 SRT 文件"
        ),
        "gapped target subtitle SRT file used for gapped translation": (
            "用于缺口翻译的含缺失项目标字幕 SRT 文件"
        ),
        "guide subtitle SRT file used for gapped or guided translation": (
            "用于缺口或引导式翻译的参考字幕 SRT 文件"
        ),
        (
            "rows to include: all or unverified; all includes every translation; "
            "unverified includes cases not marked verified (default: %(default)s)"
        ): (
            "要包含的行：all 表示每个翻译，unverified 表示未标记为已验证的案例"
            "（默认：%(default)s）"
        ),
    },
    "zh-hant": {
        "audit standard, gapped, or guided subtitle translations": (
            "稽核標準、缺口或引導式字幕翻譯"
        ),
        "source subtitle SRT file used for standard or guided translation": (
            "用於標準或引導式翻譯的來源字幕 SRT 檔"
        ),
        "gapped target subtitle SRT file used for gapped translation": (
            "用於缺口翻譯的含缺失項目標字幕 SRT 檔"
        ),
        "guide subtitle SRT file used for gapped or guided translation": (
            "用於缺口或引導式翻譯的參考字幕 SRT 檔"
        ),
        (
            "rows to include: all or unverified; all includes every translation; "
            "unverified includes cases not marked verified (default: %(default)s)"
        ): (
            "要包含的列：all 表示每個翻譯，unverified 表示未標記為已驗證的案例"
            "（預設：%(default)s）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


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
        workflow_inputs = arg_groups["input arguments"].add_mutually_exclusive_group(
            required=True
        )
        workflow_inputs.add_argument(
            "--source",
            dest="source_path",
            type=input_file_arg(),
            help="source subtitle SRT file used for standard or guided translation",
        )
        workflow_inputs.add_argument(
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
            help="JSON file containing test cases",
        )

        # Operation arguments
        cls.add_row_filter_argument(
            parser,
            TranslationAuditFilter,
            TranslationAuditFilter.all,
            description=(
                "all includes every translation; unverified includes cases not "
                "marked verified"
            ),
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
            row_filter=row_filter,
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
        if target_path is not None and guide_path is None:
            parser.error("--guide is required with --target")

        # Perform operation
        try:
            if target_path is not None:
                assert guide_path is not None
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
            elif guide_path is not None:
                assert source_path is not None
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
            else:
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
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        cls.write_report(parser, report, outfile_path, overwrite)


if __name__ == "__main__":
    AuditTranslationCli.main()
