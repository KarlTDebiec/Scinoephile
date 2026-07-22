#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared command-line support for subtitle review audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path
from typing import ClassVar

from scinoephile.analysis.audit.review import ReviewAuditFilter
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
)
from scinoephile.core.llms import TestCase
from scinoephile.llms.review import ReviewManager

from .audit_cli_base import AuditCliBase

__all__ = ["AuditReviewCliBase"]

AUDIT_REVIEW_CLI_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "rows to include: all or changes (default: changes)": (
            "要包含的行：all 表示全部，changes 表示校对更改（默认：changes）"
        ),
        (
            "further limit rows to those containing any listed character in any "
            "input; values may be separated or combined, and simplified and "
            "traditional variants are included automatically (default: no "
            "character filter)"
        ): (
            "进一步仅包含任一输入中含有所列字符的行；字符可分开或合并输入，"
            "并自动包含简繁体变体（默认：无字符筛选）"
        ),
    },
    "zh-hant": {
        "rows to include: all or changes (default: changes)": (
            "要包含的列：all 表示全部，changes 表示校對變更（預設：changes）"
        ),
        (
            "further limit rows to those containing any listed character in any "
            "input; values may be separated or combined, and simplified and "
            "traditional variants are included automatically (default: no "
            "character filter)"
        ): (
            "進一步僅包含任一輸入中含有所列字元的列；字元可分開或合併輸入，"
            "並自動包含簡繁體變體（預設：無字元篩選）"
        ),
    },
}
"""Localized shared help text keyed by locale and English source text."""


class AuditReviewCliBase(AuditCliBase):
    """Shared command-line support for subtitle review audits."""

    localizations = AUDIT_REVIEW_CLI_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""
    row_filter_help: ClassVar[str] = (
        "rows to include: all or changes (default: changes)"
    )
    """Help text for the workflow's supported row filters."""
    row_filters: ClassVar[tuple[ReviewAuditFilter, ...]] = (
        ReviewAuditFilter.all,
        ReviewAuditFilter.changes,
    )
    """Row filters supported by the workflow."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add shared review-audit operation arguments to a parser.

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
        row_filter_values = ",".join(row_filter.value for row_filter in cls.row_filters)
        arg_groups["operation arguments"].add_argument(
            "--filter",
            choices=cls.row_filters,
            default=ReviewAuditFilter.changes,
            dest="row_filter",
            metavar=f"{{{row_filter_values}}}",
            type=enum_arg(ReviewAuditFilter),
            help=cls.row_filter_help,
        )
        arg_groups["operation arguments"].add_argument(
            "--characters",
            default=(),
            metavar="CHARACTER",
            nargs="+",
            help=(
                "further limit rows to those containing any listed character in any "
                "input; values may be separated or combined, and simplified and "
                "traditional variants are included automatically (default: no "
                "character filter)"
            ),
        )

    @staticmethod
    def load_review_test_cases(
        parser: ArgumentParser,
        json_path: Path | None,
    ) -> Sequence[TestCase]:
        """Load optional review test cases from JSON.

        Arguments:
            parser: parser used to report user-facing errors
            json_path: optional review JSON path
        Returns:
            loaded review test cases
        """
        if json_path is None:
            return ()
        return AuditCliBase.load_test_cases(
            parser,
            json_path,
            ReviewManager,
            workflow_name="review",
        )
