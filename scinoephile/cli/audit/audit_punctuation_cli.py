#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for transcription punctuation audits."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.analysis.audit.punctuation import (
    PunctuationAuditFilter,
    audit_punctuation,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.llms.punctuation import PunctuationManager

from .audit_cli_base import AuditCliBase

__all__ = ["AuditPunctuationCli"]

AUDIT_PUNCTUATION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit transcription punctuation decisions": "审核转写字幕标点决策",
        "reference subtitle SRT file used to guide punctuation": (
            "用于指导标点的参考字幕 SRT 文件"
        ),
        "punctuated target subtitle SRT file": "已加标点的目标字幕 SRT 文件",
        "punctuation test-case JSON file": "字幕标点测试用例 JSON 文件",
        (
            "rows to include: all, changes, or unverified; all includes every "
            "decision; changes includes punctuation or whitespace revisions; "
            "unverified includes cases not marked verified (default: %(default)s)"
        ): (
            "要包含的行：all 表示每个决策，changes 表示标点或空白调整，"
            "unverified 表示未标记为已验证的案例（默认：%(default)s）"
        ),
    },
    "zh-hant": {
        "audit transcription punctuation decisions": "稽核轉寫字幕標點決策",
        "reference subtitle SRT file used to guide punctuation": (
            "用於指導標點的參考字幕 SRT 檔"
        ),
        "punctuated target subtitle SRT file": "已加標點的目標字幕 SRT 檔",
        "punctuation test-case JSON file": "字幕標點測試案例 JSON 檔",
        (
            "rows to include: all, changes, or unverified; all includes every "
            "decision; changes includes punctuation or whitespace revisions; "
            "unverified includes cases not marked verified (default: %(default)s)"
        ): (
            "要包含的列：all 表示每個決策，changes 表示標點或空白調整，"
            "unverified 表示未標記為已驗證的案例（預設：%(default)s）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditPunctuationCli(AuditCliBase):
    """Audit transcription punctuation decisions."""

    localizations = AUDIT_PUNCTUATION_LOCALIZATIONS
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
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--reference",
            dest="reference_path",
            required=True,
            type=input_file_arg(),
            help="reference subtitle SRT file used to guide punctuation",
        )
        arg_groups["input arguments"].add_argument(
            "--target",
            dest="target_path",
            required=True,
            type=input_file_arg(),
            help="punctuated target subtitle SRT file",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            required=True,
            type=input_file_arg(),
            help="punctuation test-case JSON file",
        )

        # Operation arguments
        cls.add_row_filter_argument(
            parser,
            PunctuationAuditFilter,
            PunctuationAuditFilter.all,
            description=(
                "all includes every decision; changes includes punctuation or "
                "whitespace revisions; unverified includes cases not marked verified"
            ),
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "punctuation"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        reference_path: Path,
        target_path: Path,
        json_path: Path,
        row_filter: PunctuationAuditFilter,
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
            reference_path: reference subtitle SRT path
            target_path: punctuated target subtitle SRT path
            json_path: punctuation test-case JSON path
            row_filter: rows to include in the report
            first_index: first reference subtitle number to include
            last_index: last reference subtitle number to include
            first_block: first reference block number to include
            last_block: last reference block number to include
            outfile_path: optional Markdown output path
            overwrite: whether to overwrite an existing output file
        """
        parser = _parser or cls.argparser()

        # Read inputs
        reference = read_series(parser, reference_path)
        target = read_series(parser, target_path)
        test_cases = cls.load_test_cases(
            parser,
            json_path,
            PunctuationManager,
            workflow_name="punctuation",
        )

        # Perform operation
        try:
            report = audit_punctuation(
                reference,
                target,
                test_cases,
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
    AuditPunctuationCli.main()
