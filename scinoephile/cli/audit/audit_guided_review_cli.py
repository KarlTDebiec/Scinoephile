#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for guided subtitle review audits."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import cast

from scinoephile.analysis.guided_review_audit import (
    GuidedReviewAuditFilter,
    audit_guided_review,
)
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.llms.guided_review import (
    GuidedReviewManager,
    GuidedReviewTestCase,
)

from .audit_workflow_cli_base import AuditCliBase

__all__ = ["AuditGuidedReviewCli"]

AUDIT_GUIDED_REVIEW_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audit guide-backed subtitle block revisions": "审核参考字幕指导的分块字幕修订",
        "target subtitle SRT file used for guided review": (
            "用于参考字幕指导审核的目标字幕 SRT 文件"
        ),
        "guide subtitle SRT file used for guided review": (
            "用于指导审核的参考字幕 SRT 文件"
        ),
        "guided-review test-case JSON file": "指导审核测试用例 JSON 文件",
        "first 1-indexed target subtitle number to include, inclusive": (
            "要包含的第一个目标字幕编号（从 1 开始，包含该编号）"
        ),
        "last 1-indexed target subtitle number to include, inclusive": (
            "要包含的最后一个目标字幕编号（从 1 开始，包含该编号）"
        ),
        "rows to include: all, changes, or unverified (default: all)": (
            "要包含的行：all 表示全部，changes 表示修订，unverified 表示未验证"
            "（默认：all）"
        ),
    },
    "zh-hant": {
        "audit guide-backed subtitle block revisions": "稽核參考字幕指導的分塊字幕修訂",
        "target subtitle SRT file used for guided review": (
            "用於參考字幕指導稽核的目標字幕 SRT 檔"
        ),
        "guide subtitle SRT file used for guided review": (
            "用於指導稽核的參考字幕 SRT 檔"
        ),
        "guided-review test-case JSON file": "指導稽核測試案例 JSON 檔",
        "first 1-indexed target subtitle number to include, inclusive": (
            "要包含的第一個目標字幕編號（從 1 開始，包含該編號）"
        ),
        "last 1-indexed target subtitle number to include, inclusive": (
            "要包含的最後一個目標字幕編號（從 1 開始，包含該編號）"
        ),
        "rows to include: all, changes, or unverified (default: all)": (
            "要包含的列：all 表示全部，changes 表示修訂，unverified 表示未驗證"
            "（預設：all）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class AuditGuidedReviewCli(AuditCliBase):
    """Audit guide-backed subtitle block revisions."""

    first_index_help = "first 1-indexed target subtitle number to include, inclusive"
    """Help text describing the first selected target index."""
    last_index_help = "last 1-indexed target subtitle number to include, inclusive"
    """Help text describing the last selected target index."""
    localizations = AUDIT_GUIDED_REVIEW_LOCALIZATIONS
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
        arg_groups["input arguments"].add_argument(
            "--target",
            dest="target_path",
            required=True,
            type=input_file_arg(),
            help="target subtitle SRT file used for guided review",
        )
        arg_groups["input arguments"].add_argument(
            "--guide",
            dest="guide_path",
            required=True,
            type=input_file_arg(),
            help="guide subtitle SRT file used for guided review",
        )
        arg_groups["input arguments"].add_argument(
            "--json",
            dest="json_path",
            required=True,
            type=input_file_arg(),
            help="guided-review test-case JSON file",
        )
        arg_groups["operation arguments"].add_argument(
            "--filter",
            choices=tuple(GuidedReviewAuditFilter),
            default=GuidedReviewAuditFilter.all,
            dest="row_filter",
            metavar="{all,changes,unverified}",
            type=enum_arg(GuidedReviewAuditFilter),
            help="rows to include: all, changes, or unverified (default: all)",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "guided-review"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        target_path: Path,
        guide_path: Path,
        json_path: Path,
        row_filter: GuidedReviewAuditFilter,
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
            GuidedReviewManager,
            workflow_name="guided-review",
        )
        test_cases = [
            cast(GuidedReviewTestCase, test_case) for test_case in loaded_test_cases
        ]

        try:
            report = audit_guided_review(
                target,
                guide,
                test_cases,
                row_filter=row_filter,
                first_index=first_index,
                last_index=last_index,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        cls.write_report(parser, report, outfile_path)


if __name__ == "__main__":
    AuditGuidedReviewCli.main()
