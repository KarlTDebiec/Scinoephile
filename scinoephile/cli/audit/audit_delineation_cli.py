#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for transcription delineation audits."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.analysis.audit.delineation import (
    DelineationAuditFilter,
    audit_delineation,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.llms.delineation import DelineationManager

from .audit_cli_base import AuditCliBase

__all__ = ["AuditDelineationCli"]

AUDIT_DELINEATION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit transcription delineation decisions": "审核转写字幕边界决策",
        "reference subtitle SRT file used to guide transcription": (
            "用于指导转写的参考字幕 SRT 文件"
        ),
        "delineation test-case JSON file": "字幕边界测试用例 JSON 文件",
        "rows to include: all, changes, or unverified (default: all)": (
            "要包含的行：all 表示全部，changes 表示边界调整，unverified "
            "表示未验证（默认：all）"
        ),
    },
    "zh-hant": {
        "audit transcription delineation decisions": "稽核轉寫字幕邊界決策",
        "reference subtitle SRT file used to guide transcription": (
            "用於指導轉寫的參考字幕 SRT 檔"
        ),
        "delineation test-case JSON file": "字幕邊界測試案例 JSON 檔",
        "rows to include: all, changes, or unverified (default: all)": (
            "要包含的列：all 表示全部，changes 表示邊界調整，unverified "
            "表示未驗證（預設：all）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditDelineationCli(AuditCliBase):
    """Audit transcription delineation decisions."""

    localizations = AUDIT_DELINEATION_LOCALIZATIONS
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
            help="reference subtitle SRT file used to guide transcription",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            required=True,
            type=input_file_arg(),
            help="delineation test-case JSON file",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--filter",
            choices=tuple(DelineationAuditFilter),
            default=DelineationAuditFilter.all,
            dest="row_filter",
            metavar="{all,changes,unverified}",
            type=enum_arg(DelineationAuditFilter),
            help="rows to include: all, changes, or unverified (default: all)",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "delineation"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        reference_path: Path,
        json_path: Path,
        row_filter: DelineationAuditFilter,
        first_index: int | None,
        last_index: int | None,
        first_block: int | None,
        last_block: int | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Read inputs
        parser = _parser or cls.argparser()
        reference = read_series(parser, reference_path)
        test_cases = cls.load_test_cases(
            parser,
            json_path,
            DelineationManager,
            workflow_name="delineation",
        )

        # Perform operation
        try:
            report = audit_delineation(
                reference,
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
    AuditDelineationCli.main()
