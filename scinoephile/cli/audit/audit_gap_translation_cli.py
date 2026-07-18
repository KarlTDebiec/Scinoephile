#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for gap-translation audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from scinoephile.analysis.gap_translation_audit import (
    GapTranslationAuditFilter,
    audit_gap_translation,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
)
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.llms.gap_translation import (
    GapTranslationManager,
    GapTranslationTestCase,
)

from .audit_workflow_cli_base import AuditCliBase

__all__ = ["AuditGapTranslationCli"]

AUDIT_GAP_TRANSLATION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit translations generated for missing target subtitles": (
            "审核为缺失目标字幕生成的翻译"
        ),
        "gapped target subtitle SRT file used for gap translation": (
            "用于缺口翻译的含缺失项目标字幕 SRT 文件"
        ),
        "complete guide subtitle SRT file used for gap translation": (
            "用于缺口翻译的完整参考字幕 SRT 文件"
        ),
        "gap-translation test-case JSON file": "缺口翻译测试用例 JSON 文件",
        "first 1-indexed guide subtitle number to include, inclusive": (
            "要包含的第一个参考字幕编号（从 1 开始，包含该编号）"
        ),
        "last 1-indexed guide subtitle number to include, inclusive": (
            "要包含的最后一个参考字幕编号（从 1 开始，包含该编号）"
        ),
        "rows to include: all or unverified (default: all)": (
            "要包含的行：all 表示全部，unverified 表示未验证（默认：all）"
        ),
        "exact case difficulty levels to include (default: all)": (
            "要包含的指定测试用例难度级别（默认：all）"
        ),
    },
    "zh-hant": {
        "audit translations generated for missing target subtitles": (
            "稽核為缺失目標字幕產生的翻譯"
        ),
        "gapped target subtitle SRT file used for gap translation": (
            "用於缺口翻譯的含缺失項目標字幕 SRT 檔"
        ),
        "complete guide subtitle SRT file used for gap translation": (
            "用於缺口翻譯的完整參考字幕 SRT 檔"
        ),
        "gap-translation test-case JSON file": "缺口翻譯測試案例 JSON 檔",
        "first 1-indexed guide subtitle number to include, inclusive": (
            "要包含的第一個參考字幕編號（從 1 開始，包含該編號）"
        ),
        "last 1-indexed guide subtitle number to include, inclusive": (
            "要包含的最後一個參考字幕編號（從 1 開始，包含該編號）"
        ),
        "rows to include: all or unverified (default: all)": (
            "要包含的列：all 表示全部，unverified 表示未驗證（預設：all）"
        ),
        "exact case difficulty levels to include (default: all)": (
            "要包含的指定測試案例難度級別（預設：all）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditGapTranslationCli(AuditCliBase):
    """Audit translations generated for missing target subtitles."""

    first_index_help = "first 1-indexed guide subtitle number to include, inclusive"
    """Help text describing the first selected guide index."""
    last_index_help = "last 1-indexed guide subtitle number to include, inclusive"
    """Help text describing the last selected guide index."""
    localizations = AUDIT_GAP_TRANSLATION_LOCALIZATIONS
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
        arg_groups["input arguments"].add_argument(
            "--target",
            dest="target_path",
            required=True,
            type=input_file_arg(),
            help="gapped target subtitle SRT file used for gap translation",
        )
        arg_groups["input arguments"].add_argument(
            "--guide",
            dest="guide_path",
            required=True,
            type=input_file_arg(),
            help="complete guide subtitle SRT file used for gap translation",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            required=True,
            type=input_file_arg(),
            help="gap-translation test-case JSON file",
        )
        arg_groups["operation arguments"].add_argument(
            "--filter",
            choices=tuple(GapTranslationAuditFilter),
            default=GapTranslationAuditFilter.all,
            dest="row_filter",
            metavar="{all,unverified}",
            type=enum_arg(GapTranslationAuditFilter),
            help="rows to include: all or unverified (default: all)",
        )
        arg_groups["operation arguments"].add_argument(
            "--difficulty",
            default=(),
            dest="difficulties",
            metavar="LEVEL",
            nargs="+",
            type=int_arg(min_value=0),
            help="exact case difficulty levels to include (default: all)",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "gap-translation"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        target_path: Path,
        guide_path: Path,
        json_path: Path,
        difficulties: Sequence[int],
        row_filter: GapTranslationAuditFilter,
        first_index: int | None,
        last_index: int | None,
        outfile_path: Path | None,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        cls.validate_range(parser, first_index, last_index)
        target = read_series(parser, target_path)
        guide = read_series(parser, guide_path)
        loaded_test_cases = cls.load_test_cases(
            parser,
            json_path,
            GapTranslationManager,
            workflow_name="gap-translation",
        )
        test_cases = [
            cast(GapTranslationTestCase, test_case) for test_case in loaded_test_cases
        ]

        try:
            report = audit_gap_translation(
                target,
                guide,
                test_cases,
                difficulties=difficulties,
                row_filter=row_filter,
                first_index=first_index,
                last_index=last_index,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        cls.write_report(parser, report, outfile_path)


if __name__ == "__main__":
    AuditGapTranslationCli.main()
