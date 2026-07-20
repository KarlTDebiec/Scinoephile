#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared command-line support for subtitle audits."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path
from typing import ClassVar

from scinoephile.analysis.review_audit import ReviewAuditFilter
from scinoephile.cli.helpers.blocks import add_block_range_args
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    int_arg,
    output_file_arg,
)
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.llms import Manager, TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converter
from scinoephile.llms.review import ReviewManager

__all__ = [
    "AuditCliBase",
    "AuditWorkflowCliBase",
]

AUDIT_WORKFLOW_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一个字幕编号（从 1 开始，包含该编号）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最后一个字幕编号（从 1 开始，包含该编号）"
        ),
        "first 1-indexed workflow block number to include, inclusive": (
            "要包含的第一个工作流区块编号（从 1 开始，包含该编号）"
        ),
        "last 1-indexed workflow block number to include, inclusive": (
            "要包含的最后一个工作流区块编号（从 1 开始，包含该编号）"
        ),
        "rows to include: all or changes (default: changes)": (
            "要包含的行：all 表示全部，changes 表示校对更改（默认：changes）"
        ),
        (
            "characters to match in any input; values may be separated or combined, "
            "and simplified and traditional variants are included automatically "
            "(default: no character filter)"
        ): (
            "要在任一输入中匹配的字符；字符可分开或合并输入，并自动包含简繁体"
            "变体（默认：无字符筛选）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 输出文件路径（默认：标准输出）"
        ),
        "overwrite outfile if it exists": "覆盖已存在的输出文件",
    },
    "zh-hant": {
        "first 1-indexed subtitle number to include, inclusive": (
            "要包含的第一個字幕編號（從 1 開始，包含該編號）"
        ),
        "last 1-indexed subtitle number to include, inclusive": (
            "要包含的最後一個字幕編號（從 1 開始，包含該編號）"
        ),
        "first 1-indexed workflow block number to include, inclusive": (
            "要包含的第一個工作流程區塊編號（從 1 開始，包含該編號）"
        ),
        "last 1-indexed workflow block number to include, inclusive": (
            "要包含的最後一個工作流程區塊編號（從 1 開始，包含該編號）"
        ),
        "rows to include: all or changes (default: changes)": (
            "要包含的列：all 表示全部，changes 表示校對變更（預設：changes）"
        ),
        (
            "characters to match in any input; values may be separated or combined, "
            "and simplified and traditional variants are included automatically "
            "(default: no character filter)"
        ): (
            "要在任一輸入中搜尋的字元；字元可分開或合併輸入，並自動包含簡繁體"
            "變體（預設：無字元篩選）"
        ),
        "Markdown outfile path (default: stdout)": (
            "Markdown 輸出檔路徑（預設：標準輸出）"
        ),
        "overwrite outfile if it exists": "覆寫已存在的輸出檔",
    },
}
"""Localized shared help text keyed by locale and English source text."""


class AuditCliBase(ScinoephileCliBase):
    """Shared command-line support for subtitle audits."""

    first_index_help: ClassVar[str] = (
        "first 1-indexed subtitle number to include, inclusive"
    )
    """Help text describing the first selected subtitle index."""
    last_index_help: ClassVar[str] = (
        "last 1-indexed subtitle number to include, inclusive"
    )
    """Help text describing the last selected subtitle index."""
    localizations = AUDIT_WORKFLOW_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add shared range and output arguments to a parser.

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
        arg_groups["operation arguments"].add_argument(
            "--first-index",
            type=int_arg(min_value=1),
            help=cls.first_index_help,
        )
        arg_groups["operation arguments"].add_argument(
            "--last-index",
            type=int_arg(min_value=1),
            help=cls.last_index_help,
        )
        add_block_range_args(
            arg_groups["operation arguments"],
            first_help=("first 1-indexed workflow block number to include, inclusive"),
            last_help="last 1-indexed workflow block number to include, inclusive",
        )
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
            help="Markdown outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @staticmethod
    def get_character_variants(characters: Sequence[str]) -> tuple[str, ...]:
        """Get requested characters and their simplified/traditional variants.

        Arguments:
            characters: requested character strings
        Returns:
            sorted individual character variants
        """
        chars = "".join(characters)
        variants = set(chars)
        variants.update(get_zho_converter(OpenCCConfig.s2t).convert(chars))
        variants.update(get_zho_converter(OpenCCConfig.t2s).convert(chars))
        return tuple(sorted(variants))

    @staticmethod
    def load_test_cases(
        parser: ArgumentParser,
        json_path: Path,
        manager_cls: type[Manager],
        *,
        workflow_name: str,
    ) -> list[TestCase]:
        """Load test cases from workflow JSON.

        Arguments:
            parser: parser used to report user-facing errors
            json_path: test-case JSON path
            manager_cls: manager defining the test-case model
            workflow_name: workflow name used in errors
        Returns:
            loaded test cases
        """
        try:
            return load_test_cases_from_json(
                json_path,
                manager_cls,
                manager_cls.base_prompt,
            )
        except (KeyError, OSError, TypeError, UnicodeError, ValueError) as exc:
            parser.error(f"Unable to load {workflow_name} JSON: {exc}")

    @staticmethod
    def validate_range(
        parser: ArgumentParser,
        first_index: int | None,
        last_index: int | None,
    ):
        """Validate an optional inclusive subtitle range.

        Arguments:
            parser: parser used to report user-facing errors
            first_index: first included one-based subtitle index
            last_index: last included one-based subtitle index
        """
        if (
            first_index is not None
            and last_index is not None
            and first_index > last_index
        ):
            parser.error("--first-index must be less than or equal to --last-index")

    @staticmethod
    def write_report(
        parser: ArgumentParser,
        report: str,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Write a report to stdout or a file.

        Arguments:
            parser: parser used to report user-facing errors
            report: Markdown report
            outfile_path: optional output file path
            overwrite: whether to overwrite an existing output file
        """
        if outfile_path is None:
            if overwrite:
                parser.error("--overwrite may only be used with --outfile")
            print(report, end="")
            return
        if outfile_path.exists() and not overwrite:
            parser.error(f"File exists: {outfile_path}; use --overwrite to replace it")
        try:
            outfile_path.write_text(report, encoding="utf-8")
        except OSError as exc:
            parser.error(str(exc))


class AuditWorkflowCliBase(AuditCliBase):
    """Shared command-line support for subtitle review audit workflows."""

    localizations = AUDIT_WORKFLOW_LOCALIZATIONS
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
        """Add shared operation and output arguments to a parser.

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
                "characters to match in any input; values may be separated or "
                "combined, and simplified and traditional variants are included "
                "automatically (default: no character filter)"
            ),
        )

    @staticmethod
    def load_review_cases(
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
